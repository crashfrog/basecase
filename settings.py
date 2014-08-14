DEFAULT_PATH_ROOT = '/shared/gn3/Basecase'
DEFAULT_INPUT_DIR = '/data/'
DEFAULT_OUTPUT_DIR = '/output/'
API = '/api/v1/'
DOCKER_REPOSITORY_HOST = 'localhost'
DOCKER_REPOSITORY_PORT = 5000

WORKER_CONFIGS = {
	'BCWorker':{
		'base_url':'unix://var/run/docker.sock',
		'version':'1.12',
		'timeout':10
	}
}