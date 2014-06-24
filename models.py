from django.db import models
from events.models import JsonField
import datetime

# Create your models here.

class JobType(models.model):
	"Job type metamodel"

	name = models.CharField(max_length=255, unique=True)
	description = models.TextField(blank=True, null=False)
	citation = models.TextField(blank=True, null=True)
	
	#celery_call = models.CharField(max_length=255, default='debug.test')
	prototype = JsonField('A JSON structure of parameter arguments and defaults for jobs of this type.', blank=True)
	
	inputs = JsonField(default=lambda: {'file extensions':['.fastq', '.fastq.gz'], 'directory':False})
	
	def __init__(self, *args, **kwargs):
		"Method override to capture changes on prototype field."
		super(JobType, self).__init__(*args, **kwargs)
		self.old_prototype = self.prototype
	
	def save(self, *args, **kwargs):
		"Method override so that child events inherit changes to prototype."
		if self.old_prototype != self.prototype:
			for job in self.job_set:
				for key, default_value in self.prototype.items():
					if key not in job.parameters:
						job.parameters[key] = default_value
						job.save()
		super(JobType, self).save(*args, **kwargs)
		
	def spawn(self, status='ready', **kwargs):
		params = dict()
		for key,default in prototype.items():
			if key in kwargs:
				params[key] = kwargs[key]
				del kwargs[key]
			else:
				params[key] = default
		return Job.objects.create(job_type=self, status=status, parameters=params, **kwargs)
	
class Job(models.model):
	
	job_type = models.ForeignKey(JobType)
	
	status = models.CharField(max_length=255, choices=[('ready','Ready to execute.'),
													   ('priority','Ready to execute at elevated priority.'),
													   ('running','Running.'),
													   ('exception','This step terminated with a fatal exception.'),
													   ('hold','Suspend execution of job.'),
													   ('finished','Job completed with no errors.')])
													   
	log_text = models.TextField(blank=True, null=True)
	
	
	parameters = JsonField(blank=True)
	result = JsonField(blank=True)
	
	predicate = models.ForeignKey('self', null=True, related_name='subsequents')
	resources = models.ManyToManyField('Resource')
	
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
		if predicate:
			return predicate.chain_id()
		return self.pk
		
	def is_ready(self):
		if predicate:
			return ('finished' in predicate.status and ('ready' in self.status or 'priority' in self.status))
		return ('ready' in self.status or 'priority' in self.status)
		
	def pass_along(self, path_list):
		"Method to pass to subsequent job(s) any resources created by this job."
		import os.path
		for job in self.subsequents:
			for path in path_list:
				if os.isdir(path):
					if job.job_type.inputs['directory']:
						resource, c = Resource.objects.get_or_create(...)
						job.resources.add(resource)
				else:
					if any([lambda f: f in path for f in job.job_type.inputs['file extensions']]):
						resource, c = Resource.objects.get_or_create(...)
						job.resources.add(resource)
	
	def log(self, message):
		"Simple logging function."
		time = datetime.datetime.now().ctime()
		for line in message.split("\n"):
			if line:
				self.log_text = self.log_text + "[{:^24}] {}\n".format(time, line)
				time = '--'
		self.save()
		
	def start(self)
		"Method to parse celery call and begin job execution."
		self.status = 'running'
		self.save()
		import basecase.functions
		tokens = self.job_type.celery_call.split(".")
		tokens.reverse()
		def recursive_getattr(module, tokens)
			if len(tokens) == 1:
				return getattr(module, tokens[0])
			token = tokens.pop()
			return recursive_getattr(getattr(module, token), tokens)
			
		
			
			
		recursive_getattr(basecase.functions, tokens).delay(**self.parameters)
	
	def finish(*args, **kwargs):
			
		self.status = 'finished'
		self.save()
		for job in self.subsequents:
			job.start()
			
			
class DataPoint(models.model):
	"CPU, memory, disk usage monitoring data point, created by remote worker threads for job-resource analysis."
	job = models.ForeignKey(Job)
	timepoint = models.DateTimeField()
	cpu = models.IntegerField("cores x load", default=0)
	memory = models.IntegerField("memory usage in bytes", default=0)
	disk_usage = models.IntegerField("Usage of temp dir in bytes", default=0)

	
class Resource(models.model):
	
	location = 
	temporary = models.BooleanField('Whether this resource should be deleted after chain is complete.', default=False)
	
class AnalysisStep(models.model):
	"Analysis workflow default object."
	job_type = models.ForeignKey(JobType)
	predicate = models.ForeignKey('self', null=True, related_name='subsequents')
	defaults = JsonField(blank=True)
	
	def spawn(self, status='ready', **kwargs):
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
	
	
	
class Analysis(models.model):
	"An analysis is a prototype for a chain of jobs."
	name = models.CharField('A short name for this analysis workflow.', max_length=255)
	description = models.TextField('An explanitory description of this analysis workflow.')
	analysis_head = models.OneToOneField(AnalysisStep)
	
	def spawn(self, status='ready', **kwargs):
		self.analysis_head.spawn(status, **kwargs).start()
	