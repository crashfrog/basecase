from django.test import TestCase

# Create your tests here.

from basecase.models import *

jobtype_args = {'name':'TestJobType',  'prototype':[{'test_arg':'foo', 'test_arg2':'bar'}, 'baz']}

class JobTypeTest(TestCase):
	
	def setUp(self):
		
		self.test_jobtype = JobType(**jobtype_args)
		
	def test_instantiation(self):
		
		self.assertEquals(self.test_jobtype.name, 'TestJobType')
		
class TestSpawn(TestCase):

	def setUp(self):
	
		self.test_jobtype = JobType(**jobtype_args)
		self.test_jobtype2 = JobType(name='TestNextJob', 'prototype':[{'step_arg':'foo'}, 'bar'])
		self.step2 = AnalysisStep(job_type=self.test_jobtype2)
		self.step1 = self.step2.predicate.create(job_type=self.test_jobtype, defaults=[{'test_arg':'qux', 'test_arg2':'quux'}, 'baz', 'corge'])
		self.head = Analysis(name='TestAnalysis', description='test description', analysis_head=self.step1)
		
	def testAcyclic(self):
		assertFalse(self.head.is_cyclic())
		
	def testChain(self):
		assertEquals(self.head.analysis_head.subsequents[0], self.step2)
		
	def testSimpleSpawn(self):
		job = self.head.spawn()
		assertEquals(job.type, self.test_jobtype)
		assertEquals(job.parameters[0]['test_arg'], 'qux')
		
	def testComplexSpawn(self):
		job = self.head.spawn('priority pending', 'test_arg':'baz', 'step_arg':'qux', )
		
		
