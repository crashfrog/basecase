#Django config for BaseCase.

import django.conf

if not django.conf.settings.ROOT_URLCONF:
	django.conf.settings.ROOT_URLCONF = 'basecase.api'

from basecase_config import *
