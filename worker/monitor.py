from threading import Thread, Event
import docker
import requests
import datetime
import time

class BCWorkerMonitor(Thread):

	def __init__(self, job, workunit, prefs):
		self.sigquit = Event()
		self.workunit = workunit
		self.prefs = prefs
		self.job = job
		self.started = datetime.datetime.now()

	def run(self):
		while not self.sigquit.is_set():
			#monitor resource consumption of running container
			datapoint = {
							'timepoint':datetime.datetime.now() - self.started,
							'cpu':0,
							'memory':0,
							'disk_usage':0,
							'message':''
			}
			requests.post(self.prefs['api'] + self.job['datapoints'], datapoint)
			if not self.sigquit.is_set():
				time.sleep(100)
			

	def quit(self):
		self.sigquit.set()