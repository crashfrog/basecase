from django.db import models
from jobs import Job, Resource
from analyses import AnalysisStep

class FunctorType(models.Model):
	
	instance_name = models.CharField("Name of monad class instance", max_length=255)
	
	
class FunctorBind(models.Model):

	monad_type = models.ForeignKey(MonadType)
	entry = models.ForeignKey(AnalysisStep)
	exit = models.ForeignKey(AnalysisStep)
	
	kwargs = JsonField()
	
	def spawn(self, *args):
		pass
	
class Functor(models.Model):

	entry = models.ForeignKey(Job)
	exit = models.ForeignKey(Job)
	resources = models.ManyToManyField(Resource)
	functor_type = models.ForeignKey(FunctorType)
	kwargs = JsonField()
	
	@property
	def module(self):
		"get the module this model object is from"
	
	def__call__(self):
		getattr(self.module, self.functor_type.instance_name)(entry, exit, resources, **self.kwargs)
		
		
class Pass():
	def __call__(self, entry, exit, resources, *args, **kwargs):
		"the identity functor"
		pass
		
class Fanout():
	def __call__(self, entry, exit, resources, *args, **kwargs):
		"the Map functor"
		pass

class Fanin():
	def __call__(self, entry, exit, resources, *agrs, **kwargs):
		"the unMap functor, I guess"
		pass
		
class UnixPipe():
	def __call__(self, entry, exit, resources, *args, **kwargs):
		"the Unix Pipe functor"
		pass
		
class Filter():
	def __call__(self, entry, exit, resources, pattern, *args, **kwargs):
		"a filtering functor"
		pass