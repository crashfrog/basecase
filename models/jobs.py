class Walkable(object):
	"Abstract base class mixin for acyclic directed graphs and trees"
	
	def walk(self, func):
		func(self)
		try:
			for s in self.subsequents:
				func(s)
		except AttributeError:
			return AttributeError("Object of class '{}' has no 'subsequents' attribute.".format(type(self)))
			
	def subset(self):
		s = {self} #a set containing this object
		for wb in self.subsequents:
			s = s + wb.subset()
		return s

	
class Job(models.Model, Walkable):
	
	job_type = models.ForeignKey(JobType)
	analysis = models.ForeignKey('Analysis', related_name='spawned_jobs', null=True)
	status = models.CharField(max_length=255, choices=[('pending', 'Initial state - ready to be packaged into a work unit.'),
													   ('priority pending', 'Package first and execute at elevated priority.'),
													   ('ready','Ready to execute.'),
													   ('priority','Ready to execute at elevated priority.'),
													   ('running','Running.'),
													   ('exception','This step terminated with a fatal exception.'),
													   ('hold','Suspend execution of job.'),
													   ('finished','Job completed with no errors.')])
													   
	log_text = models.TextField(blank=True, null=True)
	workunit = models.TextField('name of docker image workunit', blank=True, null=True)
	
	parameters = JsonField(blank=True)
	#result = JsonField(blank=True)
	
	predicates = models.ManyToManyField('self', null=True, related_name='subsequents', symmetrical=False) #this is a directed acyclic graph
	resources = models.ManyToManyField('Resource')
	
	#provenance = models.TextField(blank=True, null=True)
	
	started = models.DateTimeField(null=True, blank=True)
	finished = models.DateTimeField(null=True, blank=True)
	
	
	@property
	def elapsed(self):
		if self.started and self.finished:
			return self.finished - self.started
		elif self.started:
			return datetime.datetime.now() - self.started
		else:
			return False
	
	
	def chain_id(self):
		"Recursive method to find id of the chain this job is in; used for tempfiles, cache directories, etc."
		if self.predicates:
			return self.predicates[0].chain_id()
		return self.pk
		
	def is_ready(self):
		if self.predicates:
			return (all([lambda p: 'finished' in p.status for p in self.predicates]) and ('pending' in self.status))
		return ('pending' in self.status)

	def command(self):
		from django.template.loader import render_to_string
		context = {'resources':self.resources,
				   'output':basecase.settings.DEFAULT_OUTPUT_DIR,
				   'flags':self.parameters[0],
				   'options':self.parameters[1]}
		cmd = render_to_string(self.job_type.command_template, context)
	
	def log(self, message):
		"Simple logging function."
		time = datetime.datetime.now().ctime()
		for line in message.split("\n"):
			if line:
				self.log_text = self.log_text + "[{:^24}] {}\n".format(time, line)
				time = '--'
		self.save()
		

	def attach_resource(self, filename, stream_handle, temporary=False, checksum=''):
		"Convenience function to attach file to job"
		import os
		import os.path
		import hashlib

		default_file_root = basecase.settings.DEFAULT_PATH_ROOT

		filedir = os.path.join(default_file_root, "jobchain_{}".format(self.chain_id))
		if not os.path.exists(filedir):
			os.mkdir(filedir)
			
		resource = self.resources.create(real_location=filedir, temporary=temporary)
		with open(os.path.join(filedir, filename), 'rb') as resource_file:
			sum = hashlib.md5()
			for block in stream_handle.read(1048576):
				resource_file.write(block)
				sum.update(block)
		if checksum and not sum.hexdigest() in checksum:
			raise IOError('transfer failed checksum')
		else:
			resource.checksum = sum.hexdigest()
			
	def build_workunit(self):
		if not self.job_type.shortwork:
			import tarfile
			import tempfile
			import subprocess
			import os, os.path
			from django.template.loader import render_to_string
			import docker
			import json
		
			stage = os.path.join(basecase.settings.DEFAULT_PATH_ROOT, 'workunits', self.chain_id(), self.pk)
	# 		try:
	# 			temparchive = tempfile.TemporaryFile(dir='/run/shm')
	# 		except:
	# 			temparchive = tempfile.TemporaryFile()
	# 			
	# 		with tarfile.open(fileobj=temparchive, mode='w:bz2') as workunit:
	# 			for resource in self.job_type.binaries:
	# 				workunit.add(resource.real_location, 
	# 							 arcname=os.path.join('binaries', os.path.split(resource.real_location)[0]))
	# 			for resource in self.resources:
	# 				workunit.add(resource.real_location, 
	# 							 arcname=os.path.join('resources', os.path.split(resource.real_location)[0]))
	# 		temparchive.flush()
	# 		with open(os.path.join(default_workunit_staging, 'job_{}.sh'.format(self.pk)), 'w') as workunit:
	# 			commands = list()
	# 			#parse job and job prototype into workunit shell#
	# 			workunit.write(render_to_string('workunit.sh', {'commands':commands}))
	# 		subprocess.check_call('cat {} >> {}/job_{}.sh'.format(temparchive.name, default_workunit_staging, self.pk))
	# 		temparchive.close()

	#		do this with Docker instead

			if not os.path.exists(stage):
				os.makedirs(stage)
			
			context = {'job':self,
					   'job_type',self.job_type,
					   'config':basecase.settings}
			dockerfile_path = os.path.join(stage, 'Dockerfile')
			with open(dockerfile_path, 'r') as dockerfile:
				dockerfile.write(render_to_string('build_template.dockerfile', context))
				
			client = docker.Client(base_url='unix://var/run/docker.sock',
								   version='1.12',
								   timeout=10)
			self.workunit = '{}:{}/job{}'.format(
						basecase.settings.DOCKER_REPOSITORY_HOST,
						basecase.settings.DOCKER_REPOSITORY_PORT,
						self.pk)

			try:
				for m in client.build(stage, tag=self.workunit):
					self.log(json.loads(m)['stream'])
				for m in client.push(self.workunit):
					self.log(json.loads(m)['stream'])
			except Exception:
				pass #actually do things here
			if 'priority' in self.status:
				self.status = 'priority'
			else:
				self.status = 'ready'
		else:
			#do the shortwork, whatever that is, usually some kind of fan-in or out
			
			self.status = 'finished'
			self.save()

	def get_absolute_url(self, subpath=''):
		#return 'basecase' + basecase.settings.API + 'job/{}/{}'.format(self.pk, subpath)
		return reverse('job_endpoint', {'job_id':self.pk})


	def json(self):
		return {
			'id':self.pk,
			'analysis':self.analysis.get_absolute_url(),
			'name':self.job_type.name,
			'status':self.status,
			'workunit_url':workunit,
			'output_dir':basecase.settings.DEFAULT_OUTPUT_DIR,
			'datapoints':reverse("job_datapoints_endpoint", {'job_id':self.pk}),
			'logging_url':reverse("log_endpoint", {'job_id':self.pk})
		}
			
class DataPoint(models.Model):
	"CPU, memory, disk usage monitoring data point, created by remote worker threads for job-resource analysis."
	job = models.ForeignKey(Job)
	timepoint = models.DateTimeField()
	cpu = models.IntegerField("cores x load", default=0)
	memory = models.IntegerField("memory usage in bytes", default=0)
	disk_usage = models.IntegerField("Usage of temp dir in bytes", default=0)
	message = models.CharField(max_length=255, null=True, blank=True)

	def json(self):
		return {
			'id':self.pk,
			'job':self.job.get_absolute_url(),
			'timepoint'self.timepoint,
			'cpu':self.cpu,
			'memory':self.memory,
			'disk_usage':self.disk_usage,
			'message':self.message,
			'formats':[]
		}
	def get_absolute_url(self):
		#return 'basecase' + basecase.settings.API + 'datapoint/{}'
		return reverse('datapoint_endpoint', {'job_id':self.job.pk, 'datapoint_id':self.pk})
	
class Resource(models.Model):
	
	real_location = models.TextField(null=True, blank=True)
	#virtual_location = models.TextField(null=True, blank=True)
	temporary = models.BooleanField('Whether this resource should be deleted after chain is complete.', default=False)
	checksum = models.CharField(max_length=32)
	
	def delete(self, *a, **k):
		import shutil, os, os.path
		if temporary:
			try:
				if os.path.isdir(real_location):
					shutil.rmtree(real_location)
				else:
					os.remove(real_location)
			except:
				pass
		super(models.Model, self).__del__(self)