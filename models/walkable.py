class Walkable(object):
	"Abstract base class mixin for acyclic directed graphs and trees"
	
	def walk(self, func):
		func(self)
		try:
			for s in self.subsequents.all():
				func(s)
		except AttributeError:
			return AttributeError("Object of class '{}' has no 'subsequents' attribute.".format(type(self)))
			
	def subset(self):
		s = {self} #a set containing this object
		for wb in self.subsequents.all():
			s = s + wb.subset()
		return s
