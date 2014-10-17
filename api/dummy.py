version = 0 #dummy test API

urls.urlpatterns += patterns( #monkeypatch in the API endpoint
	url('^test', include('basecase.api.dummy'))
	)