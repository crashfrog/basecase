version = 1

from django.conf.urls import include, patterns, url

import urls
import basecase.settings
from django.http import HttpResponse
from basecase import models
import json

urls.urlpatterns += patterns( #monkeypatch in the API endpoint
	url('^{}'.format(basecase.settings.API), include('basecase.api'))
	)

urlpatterns = patterns(

	url(r"config/(?P<worker_conf>/$", config)

	url(r"jobs/$", jobs),
	url(r"jobs/id/(?P<job_id>\S+)/$", jobs, name="job_endpoint"),
	url(r"jobs/id/(?P<job_id>\S+)/files/$", job_files, name="job_files_endpoint"),

	url(r"jobs/next/$", get_next),

	url(r"jobs/id/(?P<job_id>\S+)/datapoints/$", datapoints, name="job_datapoints_endpoint"),
	url(r"jobs/id/(?P<job_id>)\S+)/datapoints/(?P<datapoint_id>\S+)/$", datapoints, name="datapoint_endpoint"),
	url(r"jobs/id/(?P<job_id>)\S+)/datapoints/(?P<datapoint_id>\S+)/(?P<format>\S+)/$", datapoints)

	url(r"jobs/id/(?P<job_id>)\S+)/logs/$", logs, name="log_endpoint"),
	
	url(r"jobs/id/(?P<job_id>)\S+)/finish/$", job_finish, name="finish_endpoint"),

	url(r"jobtypes/$", jobtypes),
	url(r"jobtypes/id/(?P<jobtype_id>)\S+)/$", jobtypes, name="jobtype_endpoint"),
	url(r"jobtypes/id/(?P<jobtype_id>)\S+)/jobs", jobs_list),

	url(r"analyses/$", analyses),
	url(r"analyses/id/(?P<analysis_id>)\S+)/$", analyses, name="analyses_endpoint"),
	
	url(r"analyses/step/id/(?P<step_id>\S+)", analysis_steps, name="steps_endpoint"),
	url(r"analyses/step/id/(?P<entry_id>\S+)/bind/(?P<exit_id>\S+)/$", binds, name="bind_endpoint"),
	
	

	)

def config(request, worker_conf="BCWorker"):
	if request.method == 'GET':
		try:
			return HttpResponse(basecase.settings.WORKER_CONFIGS[worker_conf], content_type='application/json')
		except KeyError:
			return HttpResponseNotFound()
	return HttpResponsNotAllowed(['GET',])

def jobtypes(request, jobtype_id=None):
	if jobtype_id:
		pass
	elif:
		pass

def jobs(request, job_id=None):
	if request.method == 'GET':
		if job_id:
			return HttpResponse(models.Job.objects.get(pk=job_id).json)
		else:
			start = request.GET.get('start_position', 0)
			number = request.GET.get('number_of_items', 100)
			order_by = request.GET.get('order_by', 'added')
			sort = request.GET.get('sort', 'ascending')
			if 'descending' in sort:
				sort = '-'
			elif 'ascending' in sort:
				sort = ''
			else:
				return HttpResponseBadRequest("'sort' must be 'ascending' or 'descending'")
			order_by = sort + order_by
			try:
				end = int(start) + int(number)
				return HttpResponse(json.dumps([j.json for j in models.Jobs.objects.all().order_by(order_by)][start:end]))
			except TypeError:
				return HttpResponseBadRequest("Invalid parameters for start_position or number_of_items")
			
			
	elif request.method == 'POST':
		try:
			return HttpRequest(status=501) #Not Yet Implemented
		except (KeyError, ValueError):
			return HttpResponseBadRequest()
	elif request.method == 'PUT':
		try:
			return HttpRequest(status=501) #Not Yet Implemented
		except (KeyError, ValueError):
			return HttpResponseBadRequest()
	elif request.method == 'DELETE':
		try:
			return HttpRequest(status=501) #Not Yet Implemented
		except (KeyError, ValueError):
			return HttpResponseBadRequest()
	else:
		return HttpResponsNotAllowed(['GET', 'POST', 'PUT', 'DELETE'])
		
def logs(job_id):
	if request.method == 'GET':
		job = models.Job.objects.get(pk=job_id)
		return HttpRequest(job.log_text)
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
	return HttpResponsNotAllowed(['GET',])

def job_files(request, job_id):
	return HttpRequest(status=501) #Not Yet Implemented
	
def job_finish(request, job_id):
	import threading #needs to run asynchronously
	job = models.Job.objects.get(pk=job_id)
	threading.Thread(lambda: job.finish()).start()

def datapoints(request, job_id, datapoint_id=None, format=None):
	return HttpResponse(status=501) #Not Yet Implemented
	if request.method == 'GET':

	elif request.method == 'PUT':

	else:
		return HttpResponseNotAllowed(['GET', 'PUT'])

def jobtypes(request, jobtype_id=None):
	return HttpRequest(status=501) #Not Yet Implemented

def analyses(request, analysis_id=None):
	return HttpRequest(status=501) #Not Yet Implemented
	
def steps(request, step_id):
	return HttpRequest(status=501) #Not Yet Implemented
	
def binds(request, entry, exit):
	if request.method == 'GET':
		return HttpRequest(status=501) #Not Yet Implemented
	elif request.method == 'POST':
		return HttpRequest(status=501) #Not Yet Implemented
	elif request.method == 'PUT':
		return HttpRequest(status=501) #Not Yet Implemented
	elif request.method == 'DELETE':
		return HttpRequest(status=501) #Not Yet Implemented
	else:
		return HttpResponseNotAllowed(['GET', 'PUT', 'POST', 'DELETE'])