from models import Walkable
from django.core.urlresolvers import reverse
from django.db import models

class SeparatedValuesField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
        super(SeparatedValuesField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value: return
        if isinstance(value, list):
            return value
        return value.split(self.token)

    def get_db_prep_value(self, value):
        if not value: return
        assert(isinstance(value, list) or isinstance(value, tuple))
        return self.token.join([unicode(s) for s in value])

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

class AnalysisStep(models.Model, Walkable):
	"Analysis workflow default object."
	job_type = models.ForeignKey(JobType)
	predicate = models.ManyToManyField('self', null=True, related_name='subsequents', symmetrical=False, through=models.FunctorBind)
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
		
	def get_args(self, argsdict):
		args = {'flags':self.job_type.prototype[0],
				'options':self.job_type.prototype[1]}
		argsdict[self.job_type.name] = args


class Analysis(models.Model):
	"An analysis is a handle for a chain of jobs."
	name = models.CharField('A short name for this analysis workflow.', max_length=255)
	description = models.TextField('An explanitory description of this analysis workflow.')
	tags = SeparatedValuesField('Comma-delimited list of tags associated with this analysis, used with the routing system')
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
	
	@property
	def json(self):
		from collections import OrderedDict
		struct = {
			'id':self.pk,
			'name':self.name,
			'description':self.description,
			'bind_endpoint':reverse
		}

		argsdict = OrderedDict()
		analysis_head.walk(lambda a: a.get_args(argsdict))

	def get_absolute_url(self):
		return reverse("analyses_endpoint", {'analysis_id':self.pk})