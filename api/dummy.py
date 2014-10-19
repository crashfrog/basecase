version = 0 #dummy test API

import v1 #some endpoints we just pass through
import json
from django.http import HttpResponse
import datetime
import basecase.settings


	
urlpatterns = patterns(

	url(r"^config/(?P<worker_conf>)/$", v1.config),
	url(r"^jobs/$", jobs),
	url(r"^jobs/id/(?P<id>\S+)/$", jobs),
	url(r"^jobs/id/(?P<id>\S+)/files/$", job_files),

	url(r"^jobs/next/$", jobs, id=True),

	url(r"^jobs/id/(?P<job_id>\S+)/datapoints/$", datapoints),
	url(r"^jobs/id/(?P<job_id>)\S+)/datapoints/(?P<id>\S+)/$", datapoints),
	url(r"^jobs/id/(?P<job_id>)\S+)/datapoints/(?P<id>\S+)/(?P<format>\S+)/$", datapoints),

	url(r"^jobs/id/(?P<id>)\S+)/logs/$", logs, name="log_endpoint"),
	
	url(r"^jobs/id/(?P<id>)\S+)/finish/$", jobs, force_as='POST'),

	url(r"^jobtypes/$", jobtypes),
	url(r"^jobtypes/id/(?P<id>)\S+)/$", jobtypes),
	url(r"^jobtypes/id/(?P<id>)\S+)/jobs", jobs, id=None),

	url(r"^analyses/$", analyses),
	url(r"^analyses/id/(?P<id>)\S+)/$", analyses),
	
	url(r"^analyses/step/id/(?P<id>\S+)", analyses),
	url(r"^analyses/step/id/(?P<id>\S+)/bind/(?P<exit_id>\S+)/$", binds),
	
	)
	
def dummy_function(json_func):
	"Function decorator to enable GET, PUT, POST, and DELETE, and getting sets vs objects"
	def wrapped_function(request, id=None, force_as=None, *args, **kwargs):
		if force_as:
			request.method = force_as
		if 'GET' in request.method or 'PUT' in request.method:
			if not id:
				return HttpResponse(json.dumps({'request':request,
												'object':[json_func(request),
														  json_func(request)]}))
			else:
				return HttpResponse(json.dumps({'request':request,
												'object':json_func(request)}))
		if request.method == 'POST':
			return HttpResponse(status=200)
		if request.method == 'DELETE':
			return HttpResponse(status=501) #not yet implemented
		return HttpResponseNotAllowed(['GET', 'POST', 'PUT', 'DELETE'])
	return wrapped_function
	
@dummy_function
def jobs_view(request):
# 		fields = ('status', )
# 		read_only_fields = ('id', 
# 							'analysis', 
# 							'name',  
# 							'added', 
# 							'started', 
# 							'finished', 
# 							'workunit', 
# 							'logging_url',
# 							'files_url',
# 							'finish_url',
# 							'predicates',
# 							)
			
	return {'status':'ready',
			'id':2,
			'name':'dummy_job',
			'added':datetime.datetime.today().strftime('%Y-%m-%d %H-%M-%S'),
			'started':None,
			'finished':None,
			'workunit':'{}:{}/job{}'.format(
						basecase.settings.DOCKER_REPOSITORY_HOST,
						basecase.settings.DOCKER_REPOSITORY_PORT,
						2),
			'logging_url':'/test/jobs/id/1/logs/',
			'files_url':'/test/jobs/id/1/files/',
			'finish_url':'/test/jobs/id/1/finish/',
			'predicates':['/test/jobs/id/0/',
						  '/test/jobs/id/1/'],
			'output_dir':'/output/',
			}
		
@dummy_function
def jobs_files(request):
# 	fields = ('checksum', 'temporary', 'resource_type', )
# 		read_only_fields = ('id', 'jobs', )
	return [{'checksum':'d41d8cd98f00b204e9800998ecf8427e',
			 'filename':'a_file.fastq',
			 'temporary':True,
			 'content':None,
			 'id':1,
			 'jobs':['/test/jobs/id/1/',
			 		'/test/jobs/id/2/']
			 },
			{'checksum':'d41d8cd98f00b204e9800998ecf8427e',
			 'filename':'another_file.fastq',
			 'temporary':True,
			 'content':None,
			 'id':2,
			 'jobs':['/test/jobs/id/1/',
			 		'/test/jobs/id/2/']}]
			
@dummy_function
def datapoints(request):
# 		fields = ('message', 'timepoint', 'cpu', 'memory', 'disk_usage')
# 		read_only_fields = ('id', 'formats', 'job')
	return {'message':'a test datapoint message.',
			'timepoint':datetime.datetime.today().isoformat(),
			'cpu':0.8,
			'memory':16232,
			'disk_usage':12800000,
			'id':1,
			'formats':'json',
			'job':'/test/jobs/id/1/'}
	
@dummy_function
def logs(request):
	return """
[Fri Oct 17 09:29:39 2014] BaseSpaceDemo                 (2      )   12 samples
[Fri Oct 17 09:29:47 2014] ResequencingPhixRun           (12     )    1 samples
[Fri Oct 17 09:29:48 2014] PRJNA183850                   (1260260)  342 samples
[Fri Oct 17 09:30:48 2014] PRJNA183847                   (2105200)  140 samples
[Fri Oct 17 09:31:16 2014] FDA GnomeTrakr                (2149147)    0 samples
"""
	
@dummy_function
def jobtypes(request):
	return {'name':'test_jobtype',
			'id':1,
			'version':'1.0a',
			'category':'test',
			'description':'a test description',
			'citation':'BaseCase 2014',
			'image':'crashfrog/basecase-basic:release',
			'inputs':{'patterns':['*.test', '*.dummy'],
					  'directory':False},
			'shortwork':False}
	
@dummy_function
def analyses(request):
	return {'name':'test_analysis',
			'id':1,
			'tags':['test', 'dummy', 'another_tag'],
			'analysis_tree':[], #need to figure out how to serialize a rooted DAG
			}
	
def binds(request):
	return {'id':1,
			'entry':'/test/jobs/id/1/',
			'exit':'/test/jobs/id/2/',
			'type':'test_bind'}
			
