# Apply logic to the tasks in a project.
# (For now, the tasks can only apply on a per-project basis)
import logging
import re


logger = logging.getLogger(__name__)


class AsanaCallbacks(object):

    def __init__(self, client):
        self._client = client
        self._project_scan_callbacks = []
        self._projects_to_scan = []

    def load_config(self, config):
        if len(self._project_scan_callbacks) != 0:
            logger.info("Loading project scanning configuration")
            for scan_callback in self._project_scan_callbacks:
                logger.info("Looking for config for \"%s\"", scan_callback.__name__)
                if not scan_callback.__name__ in config:
                    logger.info("No config found for \"%s\"", scan_callback.__name__)
                    next
            callback_config = config[scan_callback.__name__]
            if not "Projects" in callback_config:
                logger.warn("No projects key in project scanning config")
                return
            projects_to_scan_urls = callback_config["Projects"]
            for project_url in projects_to_scan_urls:
                self._projects_to_scan.append(self._parse_project_url_to_id(project_url))

    
    def _parse_project_url_to_id(self, project_url):
        pair = re.match("https://app.asana.com/0/(\d+)/(list|board)", project_url)
        # TODO: we pull out if it's a list or board, is that important in this context?
        return pair.groups(0)[0]
    

    def _task_scan(self, task_id):
        for callback in self._project_scan_callbacks:
            task = self._client.tasks.find_by_id(task_id)
            callback(task, self._client)

    def on_project_scan(self, function):
        """ Register a callback for a full project scan.
        """
        self._project_scan_callbacks.append(function)


    def execute_project_scan(self):
        # TODO: there should be some limit here to keep a sane number of projects to scan.
        for project_id in self._projects_to_scan:
            logger.debug("Scanning %s", project_id)
            for task in self._client.tasks.find_by_project(project_id, fields="id"):
                self._task_scan(task[u'id'])
