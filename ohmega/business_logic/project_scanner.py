# Apply logic to the tasks in a project.
# (For now, the tasks can only apply on a per-project basis)
import logging
import re
import yaml
import six
from concurrent.futures import ThreadPoolExecutor


logger = logging.getLogger(__name__)


class ProjectScanner(object):

    def __init__(self, client):
        self._client = client
        self._project_scan_callbacks = {}
        self._config = None

    def load_config(self, config):
        if "Project Scans" in config:
            self._config = config["Project Scans"]

    def include_project_scan_operation(self, function):
        self._project_scan_callbacks[function.__name__] = function

    def apply_operations(self, task_operations):
        task = task_operations[u'task']
        operations = task_operations[u'operations']
        logger.info("Task gid %s (%s)", task[u'gid'], task[u'name'])
        task = self._client.tasks.find_by_id(task[u'gid'])
        for op_name, op_config in six.iteritems(operations):
            logger.debug("Operation %s", op_name)
            if not op_name in self._project_scan_callbacks:
                logger.warn("Can't process operation %s, no function registered with that name", op_name)
                continue
            self._project_scan_callbacks[op_name](
                    task, self._client, op_config)
        return task, True


    def execute_project_scans(self):
        if not self._config:
            logger.warn("No project scan configuration detected")
            return
        for scan_config_name, scan_config in six.iteritems(self._config):
            logger.info("Scanning job named %s", scan_config_name)
            if scan_config is None:
                logger.warn("No configuration found for project scan %s",
                        scan_config_name)
                continue
            if "Project Id" not in scan_config:
                logger.warn("No \"Project Id\" key found for %s", scan_config_name)
                continue
            # There always needs to be a project_id
            project_id = scan_config["Project Id"]
            # include_completed defaults to False, but can be overridden
            include_completed = False
            if "Include Completed" in scan_config:
                if scan_config["Include Completed"] is True:
                    logger.debug("Including completed tasks in project scan")
                    include_completed = True
            # Limit defaults to 100, but can be overridden
            limit = 100
            if "Scan Limit" in scan_config:
                logger.debug("Setting limit to %d", scan_config["Scan Limit"])
                limit = scan_config["Scan Limit"]
            # Operations define what's actually to be done on each task.
            # There's not much point in this integration if there are no operations.
            if "Operations" not in scan_config:
                logger.warn("No \"Operations\" key found for %s", scan_config_name)
                continue
            operations = scan_config["Operations"]
            if operations is None:
                logger.info("No operations in operations config; this scan will be a no-op")
                continue
            logger.debug("Scanning over project %s", project_id)
            # Don't actually use the limit param at this time, but just end
            # the iteration when we get over the count.
            tasks_processed = 0
            task_operations_maps = []
            if include_completed:
                for task in self._client.tasks.find_all(
                        project=project_id,
                        fields=['gid', 'name']):
                    if tasks_processed >= limit:
                        break
                    task_operations_maps.append({u'task': task, u'operations': operations})
                    tasks_processed += 1
            else:
                for task in self._client.tasks.find_all(
                        project=project_id,
                        completed_since="now",
                        fields=['gid', 'name']):
                    if tasks_processed >= limit:
                        break
                    task_operations_maps.append({u'task': task, u'operations': operations})
                    tasks_processed += 1
            if scan_config["Parallel"] is True:
                with ThreadPoolExecutor(max_workers=8) as executor:
                    results = executor.map(self.apply_operations, task_operations_maps)
                    for (task, result) in results:
                        logger.info(result)
            else:
                """ Serial operation """
                list(map(self.apply_operations, task_operations_maps))
            logger.info("Done with %s", scan_config_name)

