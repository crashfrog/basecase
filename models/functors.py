from django.db import models
from jobs import Job, Resource
from analyses import AnalysisStep
import fnmatch
import os.path

class FunctorType(models.Model):
	
	class_name = models.CharField("Name of functor class", max_length=255)
	
	
class FunctorBind(models.Model):

	functor_type = models.ForeignKey(FunctorType)
	entry = models.ForeignKey(AnalysisStep)
	exit = models.ForeignKey(AnalysisStep)
	
	kwargs = JsonField()
	
	def spawn(self, *args):
		pass
		
	@classmethod
	def bind(entry, exit, type):
		pass
		
	@classmethod
	def unbind(entry, exit):
		binding = FunctorBind.objects.get(entry=entry, exit=exit)
		binding.delete()
		
		
class Functor(models.Model):

	entry = models.ForeignKey(Job)
	exit = models.ForeignKey(Job)
	
	functor_type = models.ForeignKey(FunctorType)
	kwargs = JsonField()
	
	@property
	def module(self):
		"get the module this model object is from"
		
	@property
	def propagating(self):
		return getattr(self.module, self.functor_type.class_name)().propagate
	
	def__call__(self):
		if self.exit.job_type.inputs['directory']:
			#pass on all the outputs that are directories
			resources = [models.Resource.objects.get(real_location=f) for f in filter(lambda d: os.path.isdir(d), self.entry.outputs)]
		else:
			#pass on all the outputs that match any of the next job's input patterns
			resources = [models.Resource.objects.get(real_location=f) for f in set([fnmatch.filter([o.real_location for o in self.entry.outputs], pat) for pat in self.exit.job_type.inputs['patterns']])]
		getattr(self.module, self.functor_type.class_name)()(self.entry, self.exit, resources, **self.kwargs)
		
#Functors		
class Pass():

	propagate = True

	def __call__(self, entry, exit, resources, *args, **kwargs):
		"the identity functor"
		for resource in resources:
			exit.resources.add(resource)
		exit.save()
		if exit.is_ready():
			exit.status.build_workunit()
		
class Fanout():
	
	propagate = True

	def __call__(self, entry, exit, resources, by=1, *args, **kwargs):
		"the Map functor"
		import itertools
		self.functor_type = FunctorType.objects.get(class_name="Pass")
		for r in resources[:by]:
			exit.resources.add(r)
			exit.save()
		for resource_tuple in itertools.izip_longest(*[iter(resources[by:)]*by): #group resources into n-tuples where n='by', like '1 by 1', '2 by 2', etc
			exit.pk = None #duplicating the job object
			exit.resources.clear()
			for resource in resource_tuple:
				exit.resources.add()
			exit.save()
			models.Functor.objects.create(precedent=enter, subsequent=exit, functor_type=FunctorType.objects.get(class_name="Pass"))

class Fanin():

	propagate = False

	def __call__(self, entry, exit, resources, *agrs, **kwargs):
		"the unMap functor, I guess"
		for resource in resources:
			exit.resources.add(resource)
		exit.save()
		if exit.is_ready:
			exit.status.build_workunit()
		
class UnixPipe():

	propagate = True

	def __call__(self, entry, exit, resources, *args, **kwargs):
		"the Unix Pipe functor"
		pass
		
class Filter():

	propagate = True

	def __call__(self, entry, exit, resources, pattern, *args, **kwargs):
		"a filtering functor"
		pass