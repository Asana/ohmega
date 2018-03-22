# Apply logic to the tasks in a project.
# (For now, the tasks can only apply on a per-project basis)


class AsanaCallbacks(object):

    def __init__(self, client):
        self._client = client
        self._task_scanned_callbacks = []

    def task_scanned(self, task_id):
        for callback in self._task_scanned_callbacks:
            task = self._client.tasks.find_by_id(task_id)
            callback(task, self._client)

    def register_task_scanned_callback(self, function):
        self._task_scanned_callbacks.append(function)

