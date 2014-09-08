version = 1

from django.conf.urls import include, patterns, url

import urls
import basecase.settings
from django.http import HttpResponse
from basecase import models

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

def jobs(request, job_id):
	pass
	
def next(request):
	if request.method == 'GET':
		ready_jobs = models.Job.objects.filter(status='priority') or models.Job.objects.filter(status='ready')
		ready_jobs.order_by('added') #oldest first
		if not ready_jobs:
			return HttpResponse(status=204)
		return HttpResponse(ready_jobs[0].json, content_type='application/json')
	return HttpResponsNotAllowed(['GET',])

def job_files(request, job_id):
	pass
	
def job_finish(request, job_id):
	pass

def datapoints(request, job_id, datapoint_id=None, format=None):
	pass

def jobtypes(request, jobtype_id=None):
	pass

def analyses(request, analysis_id=None):
	pass
	
def steps(request, step_id):
	pass
	
def binds(request, entry, exit):
	pass