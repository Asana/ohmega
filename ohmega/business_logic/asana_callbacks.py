# Apply logic to the tasks in a project.
# (For now, the tasks can only apply on a per-project basis)


class AsanaCallbacks(object):

    def __init__(self, client):
        self._client = client
        self._task_scanned_callbacks = []

    def scan_project(self, project_id):
        for task in self._client.tasks.find_by_project(
                project_id, fields="id"):
            for callback in self._task_scanned_callbacks:
                task = self._client.tasks.find_by_id(task[u'id'])
                callback(task, self._client)

    def register_task_scanned_callback(self, function):
        self._task_scanned_callbacks.append(function)

