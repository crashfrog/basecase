#Django config for BaseCase.

import django.conf.settings

if not django.conf.settings.ROOT_URLCONF:
	django.conf.settings.ROOT_URLCONF = 'basecase.api'