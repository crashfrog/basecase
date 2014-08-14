version = 1

from django.conf.urls import include, patterns, url

urlpatterns = patterns(

	url(r"config/(?P<worker_conf>/$", config)

	url(r"jobs/$", jobs_list),
	url(r"jobs/id/(?P<job_id>\S+)/$", jobs, name="job_endpoint"),
	url(r"jobs/id/(?P<job_id>\S+)/files/$", job_files, name="job_files_endpoint"),


	url(r"jobs/id/(?P<job_id>\S+)/datapoints/$", datapoints, name="job_datapoints_endpoint"),
	url(r"jobs/id/(?P<job_id)\S+)/datapoints/(?P<datapoint_id>\S+)/$", datapoints, name="datapoint_endpoint"),
	url(r"jobs/id/(?P<job_id)\S+)/datapoints/(?P<datapoint_id>\S+)/(?P<format>\S+)/$", datapoints)

	url(r"jobs/id/(?P<job_id)\S+)/logs/$", logs, name="log_endpoint"),

	url(r"jobtypes/$", jobtypes),
	url(r"jobtypes/id/(?P<jobtype_id)\S+)/$", jobtypes, name="jobtype_endpoint"),
	url(r"jobtypes/id/(?P<jobtype_id)\S+)/jobs", jobs_list),

	url(r"analyses/$", analyses),
	url(r"analyses/id/(?P<analysis_id)\S+)/$", analyses, name="analyses_endpoint"),

	)

def config(request, worker_conf="BCWorker"):
	pass

def jobs_list(jobtype_id=None):
	if jobtype_id:
		pass
	elif:
		pass

def jobs(job_id):
	pass

def job_files(job_id):
	pass

def datapoints(job_id, datapoint_id=None, format=None):
	pass

def jobtypes(jobtype_id=None):
	pass

def analyses(analysis_id=None):
	pass