from django.db import models
from events.models import JsonField

import basecase.settings

class JobType(models.Model):
	"Job type metamodel"

	name = models.CharField(max_length=255, unique=True)
	description = models.TextField(blank=True, null=False)
	citation = models.TextField(blank=True, null=True)
	
#	binaries = models.ManyToManyField('Resource')
	
	image = models.CharField("Name or ID of the docker image for this tool.", max_length=80, unique=True)
	command_template = models.TextField("Django template for command.", help_text="""
This is rendered by Django's template engine and supplied as the default command for the job image. The context will
include at least:
The resources list (one directory, or as many files as match the patters specified in self.inputs, as absolute paths)
at 'resources',
the output path at 'output',
the flag argument list at 'flags',
the options argument list at 'options'
""")
	
	prototype = JsonField('A JSON structure of parameter arguments and defaults for jobs of this type.', blank=True, default=([], {}))
	
	inputs = JsonField(default=lambda: {'patterns':['*fastq', '*fastq.gz'], 'directory':False})
	shortwork = models.BooleanField("Shortwork job types don't farm out to workers but execute locally", default=False)
	
	def __init__(self, *args, **kwargs):
		"Method override to capture changes on prototype field."
		super(JobType, self).__init__(*args, **kwargs)
		self.old_positional_prototype = self.positional_prototype
		self.old_flag_prototype = self.positional_prototype
	
	def save(self, *args, **kwargs):
		"Method override so that child events inherit changes to prototype."
		if self.old_prototype != self.prototype:
			for job in self.job_set:
				for key, default_value in self.prototype.items():
					if key not in job.parameters:
						job.parameters[key] = default_value
						job.save()
		super(JobType, self).save(*args, **kwargs)
		
		
# 	def spawn(self, status='ready', **kwargs):
# 		params = dict()
# 		for prototype in ('positional_prototype', 'flag_prototype'):
# 			for key,default in getattr(self, prototype).items():
# 				if key in kwargs:
# 					params[key] = kwargs[key]
# 					del kwargs[key]
# 				else:
# 					params[key] = default
# 		return Job.objects.create(job_type=self, status=status, parameters=params, **kwargs)

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
	
	type = models.ForeignKey(JobType)
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
	
	provenance = models.TextField(blank=True, null=True)
	
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
			
	def prepare_workunit(self):
		if not self.job_type.shortwork:
			import tarfile
			import tempfile
			import subprocess
			import os, os.path
			from django.template.loader import render_to_string
			import docker
		
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
			try:
				self.workunit = client.build(dockerfile_path, tag='job{}'.format(self.pk))
			except Exception:
				pass #actually do things here
			if 'priority' in self.status:
				self.status = 'priority'
			else:
				self.status = 'ready'
		else:
			#do the shortwork, whatever that is, usually some kind of fan-in or out
			
			self.status = 'finished'
			
class DataPoint(models.Model):
	"CPU, memory, disk usage monitoring data point, created by remote worker threads for job-resource analysis."
	job = models.ForeignKey(Job)
	timepoint = models.DateTimeField()
	cpu = models.IntegerField("cores x load", default=0)
	memory = models.IntegerField("memory usage in bytes", default=0)
	disk_usage = models.IntegerField("Usage of temp dir in bytes", default=0)
	message = models.CharField(max_length=255, null=True, blank=True)

	
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
		

	
class AnalysisStep(models.Model, Walkable):
	"Analysis workflow default object."
	job_type = models.ForeignKey(JobType)
	predicate = models.ManyToManyField('self', null=True, related_name='subsequents', symmetrical=False)
	defaults = JsonField(blank=True)
	
	def spawn(self, status='pending', **kwargs):
		"Recursive method to create a job chain from this step in the chain."
		params = dict()
		for key,default in defaults.items():
			if key in kwargs:
				params[key] = kwargs[key]
				del kwargs[key]
			else:
				params[key] = default
		job = job_type.spawn(status, **params)
		for next_step in self.subsequents:
			job.subsequents.add(next_step.spawn(status, **kwargs))
		job.save()
		return job
		
	def is_cyclic(self, job1):
		if job1.pk == self.pk:
			return True
		if subsequents:
			return any([s.is_cyclic(job1) for s in self.subsequents])
		return False
		
	def get_args(self, argslist):
		
		
# class AnalysisController(AnalysisStep):
# 	"Flow-control analysis step; abstract singleton base class for fan-outs, switches, etc"
# 	class Meta:
# 		abstract=True
# 	#override
# 	def save(self, *args, **kwargs):
# 		self.__class__.objects.exclude(id=self.id).delete()
# 		super(AnalysisController, self).save(*args, **kwargs)
# 		
# 	@classmethod
# 	def load(cls):
# 		try:
# 			return cls.objects.get()
# 		except cls.DoesNotExist:
# 			return cls()
# 			
# class FanOut(AnalysisController):
# 	"Singleton behavior object that takes a list of resources, and spawns one job per resource."
# 	
	
class Analysis(models.Model):
	"An analysis is a handle for a chain of jobs."
	name = models.CharField('A short name for this analysis workflow.', max_length=255)
	description = models.TextField('An explanitory description of this analysis workflow.')
	analysis_head = models.OneToOneField(AnalysisStep)
	
	def get_args(self):
		"Collect a list of parameters for the analysis chain."
	
	def spawn(self, status='pending', **kwargs):
		head_job = self.analysis_head.spawn(status, **kwargs)
		self.spawned_jobs.add(head_job)
		return job
		
		
	def is_cyclic(self):
		#true-false if it contains a cycle
		sb = analysis.head.subset()
		sb.remove(analysis_head)
		return any([analysis_head.is_cyclic(s) for s in sb]) 
		
	def aggregate(self, jobs):
		"Method to produce combined, single docker image to reproduce the entire analysis."	
		pass
		
	@classmethod
	def aggregate(jobs):
		"Class method to aggregate multiple docker aggregations into a single one."
		pass