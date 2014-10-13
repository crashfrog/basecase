version = 1

from django.conf.urls import include, patterns, url

from django.views.generic import View
from django.views.generic.edit import DeletionMixin
from django.views.generic.detail import SingleObjectMixin

import urls
import basecase.settings
from django.http import HttpResponse
from basecase import models
import json

urls.urlpatterns += patterns( #monkeypatch in the API endpoint
	url('^{}'.format(basecase.settings.API), include('basecase.api'))
	)

urlpatterns = patterns(

	url(r"config/(?P<worker_conf>)/$", config),
	url(r"jobs/$", JobsView.as_view()),
	url(r"jobs/id/(?P<id>\S+)/$", JobsView.as_view(), name="job_endpoint"),
	url(r"jobs/id/(?P<id>\S+)/files/$", job_files, name="job_files_endpoint"),

	url(r"jobs/next/$", get_next),

	url(r"jobs/id/(?P<job_id>\S+)/datapoints/$", DataPointsView.as_view(), name="job_datapoints_endpoint"),
	url(r"jobs/id/(?P<job_id>)\S+)/datapoints/(?P<id>\S+)/$", DataPointsView.as_view(), name="datapoint_endpoint"),
	url(r"jobs/id/(?P<job_id>)\S+)/datapoints/(?P<id>\S+)/(?P<format>\S+)/$", DataPointsView.as_view())

	url(r"jobs/id/(?P<id>)\S+)/logs/$", logs, name="log_endpoint"),
	
	url(r"jobs/id/(?P<id>)\S+)/finish/$", job_finish, name="finish_endpoint"),

	url(r"jobtypes/$", JobTypesView.as_view()),
	url(r"jobtypes/id/(?P<id>)\S+)/$", JobTypesView.as_view(), name="jobtype_endpoint"),
	url(r"jobtypes/id/(?P<id>)\S+)/jobs", JobsView.as_view()),

	url(r"analyses/$", AnalysisView.as_view()),
	url(r"analyses/id/(?P<id>)\S+)/$", AnalysisView.as_view(), name="analyses_endpoint"),
	
	url(r"analyses/step/id/(?P<id>\S+)", AnalysisStepView.as_view(), name="steps_endpoint"),
	url(r"analyses/step/id/(?P<id>\S+)/bind/(?P<exit_id>\S+)/$", BindsView.as_view(), name="bind_endpoint"),
	
	)
	
def BasecaseObjectView(View, DeletionMixin, SingleObjectMixin):
	
	pk_url_kwarg = 'id'
				
	def post(self, request, job_id=None):
		return HttpResponse(status=501)
		
	def put(self, request):
		return HttpResponse(status=501)
		
	def delete(self, request, job_id=None):
		return HttpResponse(status=501)
	

def config(request, worker_conf="BCWorker"):
	if request.method == 'GET':
		try:
			return HttpResponse(basecase.settings.WORKER_CONFIGS[worker_conf], content_type='application/json')
		except KeyError:
			return HttpResponseNotFound()
	return HttpResponseNotAllowed(['GET',])

class JobTypesView(BasecaseObjectView):

	model = models.JobType

class JobsView(BasecaseObjectView, ListModelMixin):
	
	queryset = models.Job.objects.all().order_by('-added')
	model = models.Job
	 
class AnalysisView(BasecaseObjectView):
	
	model = models.Analysis
	
class AnalysisStepView(BasecaseObjectView):

	model = models.AnalysisStep
	
class BindsView(BasecaseObjectView):

	model = models.FunctorBind
	
class DataPointsView(BasecaseObjectView, ListModelMixin):
	
	model = models.DataPoint
	queryset = models.DataPoint.objects.filter(job=job_id)

		
def logs(job_id):
	if request.method == 'GET':
		job = models.Job.objects.get(pk=job_id)
		return HttpResponse(job.log_text)
	elif request.method == 'POST':
		job = models.Job.objects.get(pk=job_id)
		job.log(request.POST['message'])
	else:
		return HttpResponseNotAllowed(['GET', 'POST'])
	
def next(request):
	if request.method == 'GET':
		ready_jobs = models.Job.objects.filter(status='priority') or models.Job.objects.filter(status='ready')
		ready_jobs.order_by('added') #oldest first
		if not ready_jobs:
			return HttpResponse(status=204)
		return HttpResponse(ready_jobs[0].json, content_type='application/json')
	return HttpResponseNotAllowed(['GET',])

def job_files(request, job_id):
	return HttpResponse(status=501) #Not Yet Implemented
	
def job_finish(request, job_id):
	import threading #needs to run asynchronously
	job = models.Job.objects.get(pk=job_id)
	threading.Thread(lambda: job.finish()).start()

# def datapoints(request, job_id, id=None, format=None):
# 
#	if request.method == 'GET':
# 		try:
# 			return HttpResponse(status=501) #Not Yet Implemented
# 		except (KeyError, ValueError):
# 			return HttpResponseBadRequest()
# 	elif request.method == 'POST':
# 		try:
# 			return HttpResponse(status=501) #Not Yet Implemented
# 		except (KeyError, ValueError):
# 			return HttpResponseBadRequest()
# 	elif request.method == 'PUT':
# 		try:
# 			return HttpResponse(status=501) #Not Yet Implemented
# 		except (KeyError, ValueError):
# 			return HttpResponseBadRequest()
# 	elif request.method == 'DELETE':
# 		try:
# 			return HttpResponse(status=501) #Not Yet Implemented
# 		except (KeyError, ValueError):
# 			return HttpResponseBadRequest()
# 	else:
# 		return HttpResponseNotAllowed(['GET', 'POST', 'PUT', 'DELETE'])
# 		
# 
# 	
# def binds(request, entry, exit):
# 	if request.method == 'GET':
# 		try:
# 			return HttpResponse(status=501) #Not Yet Implemented
# 		except (KeyError, ValueError):
# 			return HttpResponseBadRequest()
# 	elif request.method == 'POST':
# 		try:
# 			return HttpResponse(status=501) #Not Yet Implemented
# 		except (KeyError, ValueError):
# 			return HttpResponseBadRequest()
# 	elif request.method == 'PUT':
# 		try:
# 			return HttpResponse(status=501) #Not Yet Implemented
# 		except (KeyError, ValueError):
# 			return HttpResponseBadRequest()
# 	elif request.method == 'DELETE':
# 		try:
# 			return HttpResponse(status=501) #Not Yet Implemented
# 		except (KeyError, ValueError):
# 			return HttpResponseBadRequest()
# 	else:
# 		return HttpResponseNotAllowed(['GET', 'POST', 'PUT', 'DELETE'])
