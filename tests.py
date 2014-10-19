from django.test import TestCase
from unittest import skip

# Create your tests here.

from basecase.models import *

jobtype_args = {'name':'TestJobType',  
								'prototype':[{'test_arg':'foo', 'test_arg2':'bar'}, 'baz'],
								'image':'phusion/baseimage:0.9.12'}
spades_type_args = {
	'name':'SpadesTest',
	'prototype':[{'o', '/tmp/'}, 'test'],
	'description':"Spades 3.1 internal tests",
	'image':'localhost:5000/spades:3.1',
	'command_template':"spades.py {flags} {options}",
	'shortwork':False
}

class JobTypeTest(TestCase):
	
	def setUp(self):
		
		self.test_jobtype = JobType(**jobtype_args)
		self.test_jobtype.save()
		
	def test_instantiation(self):
		
		self.assertEquals(self.test_jobtype.name, 'TestJobType')

class TestDefaultFixtures(TestCase):

	#fixtures = ('simple', )

	def testIdentityJob(self):

		self.job = JobType.objects.get(id=1)
		self.assertEquals(self.job.name, 'Identity')

	def testFunctors(self):
	
		self.assertEquals(FunctorType.objects.get(id=1).class_name, 'Pass')
		self.assertEquals(FunctorType.objects.get(id=2).class_name, 'Fanout')
		self.assertEquals(FunctorType.objects.get(id=3).class_name, 'Fanin')
		self.assertEquals(FunctorType.objects.get(id=4).class_name, 'Unix_Pipe')
		
class TestSpawn(TestCase):

	def setUp(self):
	
		self.test_jobtype = JobType.objects.create(**jobtype_args)
		self.test_jobtype2 = JobType.objects.create(name='TestNextJob', 
													prototype=[{'step_arg':'foo'}, 'bar'],
													image='ubuntu:14.04')
		self.step2 = AnalysisStep.objects.create(job_type=self.test_jobtype2)
		self.step1 = AnalysisStep.objects.create(job_type=self.test_jobtype, defaults={'test_arg':'qux', 'test_arg2':'quux'})
		self.step1.bind_by(self.step2, 'Pass')
		self.step1.save()
		self.head = Analysis.objects.create(name='TestAnalysis', description='test description', analysis_head=self.step1)
		
	def testAcyclic(self):
		self.assertFalse(self.head.is_cyclic())
		
	def testChain(self):
		self.assertEquals(len(self.head.analysis_head.subsequents.all()), 1)
		for step in self.head.analysis_head.subsequents:
			self.assertEquals(step, self.step2)
		
	def testSimpleSpawn(self):
		job = self.head.spawn()
		self.assertEquals(job.type, self.test_jobtype)
		self.assertEquals(job.parameters[0]['test_arg'], 'qux')
		
	def testComplexSpawn(self):
		job = self.head.spawn('priority pending', test_arg='baz', step_arg='qux' )
		self.assertEquals(job.status, 'priority pending')
		self.assertEquals(job.parameters[0]['test_arg'], 'baz')
		for next_job in job.subsequents.all():
			self.assertEquals(next_job.parameters[0]['step_arg'], 'qux')
			
class TestDummyUrlConf(TestCase):
	
	import api.dummy
	
	def setUp(self):
		pass
		
	def api_test(self, endpoint):
		import requests
		return requests.get(os.path.join('http://localhost/api/test/', endpoint)).json()['object']
		
	def testJobs(self):
		self.assertEquals([api.dummy.jobs_view(None), api.dummy.jobs_view(None)], api_test('/jobs/'))
		self.assertEquals(api.dummy.jobs_view(None), api_test('/jobs/id/1'))
		
	def testJobsFiles(self):
		self.assertEquals(api.dummy.jobs_files(None), api_test('/jobs/id/1/files/'))
		
	def testLogs(self):
		self.assertEquals(api.dummy.logs(None), api_test('jobs/id/1/logs'))
	
	def testJobtypes(self):
		self.assertEquals([api.dummy.jobtypes(None), api.dummy.jobtypes(None)], api_test('/jobtypes/'))
		self.assertEquals(api.dummy.jobtypes(None), api_test('jobtypes/id/1'))
		
	def testAnalyses(self):
		self.assertEquals([api.dummy.analyses(None), api.dummy.analyses(None)], api_test('/analyses/'))
		self.assertEquals(api.dummy.analyses(None), api_test('analyses/id/1'))

@skip
class TestDocker(TestCase):

	def setUp(self):
		import docker

	def testDocker(self):
		#make a container from the basecase image
		import docker

	def tearDown(self):
		import docker

@skip
class TestPreparation(TestCase):

	def setUp(self):
		import docker

	def testMakeUnit(self):
		pass



	def tearDown(self):
		import docker

@skip
class TestApiObjectRepresentation(TestCase):

	def setUp(self):
		pass

	def testApi(self):
		pass

@skip
class TestApiEndpoints(TestCase):

	def setUp(self):
		pass

	def testGET(self):
		pass

	def testPOST(self):
		pass

	def testPUT(self):
		pass

	def testUpload(self):
		pass

	def tearDown(self):
		pass

@skip
class TestSpades(TestCase):

	def setUp(self):
		pass

	def testSpades(self):
		pass
