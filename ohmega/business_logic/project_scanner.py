# Apply logic to the tasks in a project.
# (For now, the tasks can only apply on a per-project basis)
import logging
import re
import yaml


logger = logging.getLogger(__name__)


class ProjectScanningConfiguration(object):
    """Get the project scanning configuration according to the schema we expect.
    """
    def __init__(self, config):
        # There will be a top-level scope called "Project Scans" that we look
        # to in order to get our config.
        self._config_scope = None
        if "Project Scans" in config:
            self._config_scope = config["Project Scans"]
        else:
            logger.warn("No project scan configuration detected")

    def __iter__(self):
        self._iter_values = iter(self._config_scope.values())
        return self

    def next(self):
        return self._iter_values.next()


class ProjectScanner(object):

    def __init__(self, client):
        self._client = client
        self._project_scan_callbacks = []
        self._config = None

    def load_config(self, config):
        self._config = ProjectScanningConfiguration(config)

    def _task_scan(self, task_id):
        for callback in self._project_scan_callbacks:
            task = self._client.tasks.find_by_id(task_id)
            callback(task, self._client)

    def include_project_scan_operation(self, function):
        self._project_scan_callbacks.append(function)

    def execute_project_scans(self):
        for thisconfig in self._config:
            import pdb; pdb.set_trace()
            logger.info(thisconfig)
#        for project_id in self._projects_to_scan:
#            logger.debug("Scanning %s", project_id)
#            if self._include_completed:
#                for task in self._client.tasks.find_all(
#                        project=project_id,
#                        fields="id"):
#                    self._task_scan(task[u'id'])
#            else:
#                for task in self._client.tasks.find_all(
#                        project=project_id,
#                        completed_since="now",
#                        fields="id"):
#
