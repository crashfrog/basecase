import docker
import requests
import time
import os, os.path, glob, shutil
import tempfile
import json
import uuid
import monitor
import re
import subprocess

from daemon import Daemon



class BCWorker(Daemon):

	def __init__(self):
		super( Daemon, self).__init__()
		self.auth = ('basecase_worker', 'basecase_worker')
		try:
			with open("prefs.json", 'r') as prefs_file:
				self.prefs = json.load(prefs_file)
			[self.prefs[k] for k in ('api', 'client id', 'docker port', 'client pk')]
		except (IOError, OSError, KeyError):
			self.prefs = {
							"api":os.environ.get('BASECASE_MASTER', 'https://basecase.org/api/v1'),
							"client id":os.environ.get('HOSTNAME', 'Basecase_worker_{}'.format(uuid.uuid1())),
							"docker port":os.environ.get('DOCKER_PORT', 5000),
							"client pk":os.environ.get('BASECASE_PRIVATE_KEY', False)
						}
			with open("prefs.json", 'w') as prefs_file:
				json.dump(self.prefs, prefs_file, indent=2)

	def api_get(self, endpoint):
		return requests.get(os.path.join(self.prefs['api'], endpoint), auth=auth)

	def api_post(self, endpoint, *args, **kwargs):
		pass


	def run(self):

		#init docker system
		config = self.api_get('/config/BCWorker').json()
		dock = docker.Client(**config)

		while True:
			try:
			#poll for a new job
				r = self.api_get('/jobs/next')
				r.raise_for_status()
				if r.status_code == requests.codes.ok:
					stdoutput = ''
					job = r.json()['object']
					#get the job from the Basecase private Docker repo
					self.api_post(job['logging_url'], '({client_id}) *** Pulling ***'.format(**self.prefs))
					dock.pull(job['workunit_url'], tag=job['id'])
					#make the output folder
					output = tempfile.mkdirtemp()
					#start the monitor thread and run the job with the output folder attached
					m = dock.create_container(job['id'], volumes=(output, ))
					dock.start(workunit, binds={job['output_dir']:{'bind':output, 'ro':False}})
					mon = monitor.BCWorkerMonitor(job, workunit, self.prefs)
					self.api_post(job['logging_url'], '({client_id}) *** Starting ***'.format(**self.prefs))
					mon.start()
					#wait for completion
					for line in dock.logs(workunit, stream=True):
						stdoutput += line
						self.api_post(job['logging_url'], line)
					#dock.wait(workunit)
					mon.quit()
					mon.join()
					#search stdout
					with open(os.path.join(output, 'stdout.log'), 'w') as stdout_file:
						stdout_file.write(stdoutput)
						
					results = dict()
					for pattern_name, re_pattern in job['result_mask'].items():
						result = re.findall(re_pattern, stdoutput)
						results[pattern_name] = result
					
					with open(os.path.join(output, 'results.json'), 'w') as results_json:
						json.dump(results, results_json)
					
					#upload the output files
					self.api_post(job['logging_url'], '({client_id}) *** Finishing ***'.format(**self.prefs))
					for item in os.listdir(output):
						sum = subprocess.check_output('md5sum', os.path.join(output, item))[:32]
						with open(os.path.join(output, item), 'rb') as f:
							self.api_post(job['logging_url'], '({client_id}) *** Uploading {} ***'.format(item, **self.prefs))
							self.api_post(job['files_url'], files={'file':f, 'checksum':sum})
							
					#set job as finished
					self.api_post(job['finish_url'])

					#tear down the completed image
					dock.remove_container(workunit)
					dock.remove_image(job['id'])
					shutil.rmtree(output)
				#or wait for a bit
				elif r.status_code == requests.codes.no_content:
					time.sleep(1000)
				else:
					raise requests.exceptions.RequestException("Unknown response from Basecase API: {}".format(r.status_code))
			except (requests.exceptions.HTTPError, requests.exceptions.RequestException) as e:
				#do something
				raise



if __name__ == "__main__":
        daemon = BCWorker('/tmp/BCWorker.pid')
        if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
                        daemon.start()
                elif 'stop' == sys.argv[1]:
                        daemon.stop()
                elif 'restart' == sys.argv[1]:
                        daemon.restart()
                else:
                        print "Unknown command"
                        sys.exit(2)
                sys.exit(0)
        else:
                print "usage: %s start|stop|restart" % sys.argv[0]
                sys.exit(2)