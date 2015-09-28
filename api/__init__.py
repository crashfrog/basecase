# API root URL patterns
from django.conf.urls import url, include, patterns

urlpatterns = patterns(
	url(r'^api/test', include('basecase.api.dummy')),
	url(r'^api/v1', include('basecase.api.v1')),
	url(r'^api', include('basecase.api.v1')),
	url(r'^', include('basecase.client.urls')),
	)
