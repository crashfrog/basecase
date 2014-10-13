import json
from django.db import models

class JsonField(models.TextField):
#	pass
	description = "A JSON field, rendered as structured text."
 
	__metaclass__ = models.SubfieldBase
 
	def __init__(self, *args, **kwargs):
		super(JsonField, self).__init__(*args, **kwargs)
 
	def to_python(self, value):
		if isinstance(value, list) or isinstance(value, dict):
			return value
		if isinstance(value, str) or isinstance(value, unicode):
			try:
				return json.loads(value)
			except ValueError:
				return dict()
		return dict()
 
	def get_prep_value(self, value, *args, **kwargs):
		if isinstance(value, list) or isinstance(value, dict):
			return json.dumps(value, indent=2, separators=(',',':'))
		return ''
 
	def value_to_string(self, obj):
		return json.dumps(self._get_val_from_obj(obj), indent=2, separators=(',',':'))