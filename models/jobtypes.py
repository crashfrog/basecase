import basecase.settings

class JobType(models.Model):
	"Job type metamodel"

	name = models.CharField(max_length=255, unique=True)
	description = models.TextField(blank=True, null=False)
	citation = models.TextField(blank=True, null=True)
	
#	binaries = models.ManyToManyField('Resource')
	
	image = models.CharField("Name or ID of the docker image for this tool.", max_length=80, unique=True)
	command_template = models.TextField("Django template for command.", help_text="""
This is rendered by Django's template engine and supplied as the default command for the job image. The context will
include at least:
The resources list (one directory, or as many files as match the patters specified in self.inputs, as absolute paths)
at 'resources',
the output path at 'output',
the flag argument list at 'flags',
the options argument list at 'options'
""")
	
	prototype = JsonField('A JSON structure of parameter arguments and defaults for jobs of this type.', blank=True, default=([], {}))
	
	result_mask = JsonField(blank=True, default={})
	
	inputs = JsonField(default=lambda: {'patterns':['*fastq', '*fastq.gz'], 'directory':False})
	shortwork = models.BooleanField("Shortwork job types don't farm out to workers but execute locally", default=False)
	
	def __init__(self, *args, **kwargs):
		"Method override to capture changes on prototype field."
		super(JobType, self).__init__(*args, **kwargs)
		self.old_positional_prototype = self.positional_prototype
		self.old_flag_prototype = self.positional_prototype
	
	def save(self, *args, **kwargs):
		"Method override so that child events inherit changes to prototype."
		if self.old_prototype != self.prototype:
			for job in self.job_set:
				for key, default_value in self.prototype.items():
					if key not in job.parameters:
						job.parameters[key] = default_value
						job.save()
		super(JobType, self).save(*args, **kwargs)