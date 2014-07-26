# Docker buildfile autogenerated by BaseCase on {{ now 'r' }}
# 

FROM {{ job_type.image }}
MAINTAINER {{ config.instance }}, {{ config.admin }}

RUN mkdir {{ config.default_input_dir }}

{% for resource in resources %}
COPY {{ resource.real_location }} /data/
{% endfor %}

CMD {{ job.command }}