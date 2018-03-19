from abc import ABCMeta

from ohmega.services import TaskDiffService, TaskStorageService, TaskAPIService

#Apply logic to the tasks in a project.
# (For now, the tasks can only apply on a per-project basis)
class TaskLogic(Object):
    __metaclass__ = ABCMeta

    @classmethod
    def register(project_id, runner):
        """Register this as business logic with the runner. That means that whenever the runner is run, it can find all the business logic classes to initialize and run."""
        pass

    def __init__(self, project_id, client):
        self._project_id = project_id
        self._client = client
        self._storage_service = TaskStorageService()
        self._task_diff_service = TaskDiffService()
        self._task_api_service = TaskAPIService()


    def task_scanned_template(task_id):
        """Template method strategy for creating action for taskScanned - we only have the current task state."""
        now_task = self._task_api_service.get_current_task_state(task_id)

        altered_task = self.task_scanned(task)

        diff = self._task_diff_service.calculate_diff_for_tasks(now_task, altered_task)
        updated_task = self._task_api_service.patch_task(now_task, diff)
        self._storage_service.store_task(updated_task)

        @abstractmethod
    def task_scanned(now_task):
        """Subclasses should implement this method in order to take action when a task is scanned
           There is no diff passed, because this method is called when there is no information
           about the previous state of a task.
        """

    def task_changed_template(task_id):
        """Template method strategy for creating action for taskChanged - we have old and now states, and can pass this to a handler."""
        #Assume for now that we can definitely get the event from an event stream
        old_task = self._storage_service.get_stored_task(task_id)
        now_task = self._task_api_service.get_current_task_state(task_id)
        diff = self._task_diff_service.calculate_diff_for_tasks(old_task, now_task)

        altered_task = self.task_changed(old_task, diff, now_task)

        diff = self._task_diff_service.calculate_diff_for_tasks(now_task, altered_task)
        updated_task = self._task_api_service.patch_task(now_task, diff)
        self._storage_service.store_task(updated_task)

    @abstractmethod
    def task_changed(old_task, diff, now_task):
        """Subclasses should implement this method in order to take action when a task changes
           It should be assumed that the difference between the old and the new task is represented
           accurately, but that there may have been intermediate changes in the meantime. For instance,
           if the task had State A and then becomes State B, and this method is called, the diff will be
           between states A and B.
           If the task had State A, and then becomes State B, and then State C, and this method is called,
           the delta will be between states A and C.
           In other words, we can represent roughly the changes from the *last* time this script made
           a change to the task and the current state of the task (but perhaps not between).
        """

    def task_stagnant_template(task_id):
        """Template method strategy for when a task becomes stagnant - no recent changes"""
        # The intent of this is not to incur *any* restrictions on external sources (like cron) because
        # that goes against the simplicity clause. This is simply checked by this framework every time
        # major events get executed (like a new run of the CLI app, a new webhook is received).
        # Since we use a local DB, we can make this pretty reactive - we can check the last previous state
        # of the task to find if it's likely to be stale.

        # This is possible because:
        #  If we have to scan, we can scan for tasks that are older than config.stagnant or whatever. We're scanning anyway. All tasks get checked.
        #  If we don't have to scan, we would have gotten task added, and can forward them to the scan (for instance, stagnant can be 10 minutes, and we didn't run this for a day - a task got added, but can also be stagnant).
        #  If we didn't get task added, it should be in the DB insofar as deleted or checked off tasks can still
        #  be queried in the API.
        
        # Therefore, we take a double-checked-lock sort of approach: try with the cached task if it exists,
        # If it passes as stagnant, we update and try again (since it might need updating). If it's still
        # stagnant, pass it on.
        
        old_task = self._storage_service.get_stored_task(task_id)
        if self.is_task_stagnant(old_task):
            now_task = self._task_api_service.get_current_task_state(task_id)
            if self.is_task_stagnant(now_task):

                altered_task = self.task_stagnant(now_task)

                diff = self._task_diff_service.calculate_diff_for_tasks(now_task, altered_task)
                updated_task = self._task_api_service.patch_task(now_task, diff)
                self._storage_service.store_task(updated_task)

    @abstractmethod
    def is_task_stagnant(task):
        """The task *may* be stagnant. What stagnant means depends on the business logic.
           One example may be that you expect that the task needs to have, say, a comment
           placed on it every week; and if that's the requirement, you should check the
           task that we think might be stagnant in order to verify.
           
           Implementation details: note that this method might be called twice, once for a task
           that we think might be stagnant (but is old and may have been changed), and once
           after we refresh that task and need to verify it against whatever its new state is.
           This should NOT change task state (there is no delta applied from this return value,
           for instance) and should be expected to sometimes be called twice for the task in
           quick succession.
        """

    @abstractmethod
    def task_stagnant(task):
        """The task has been flagged as stagnant in some way and should be updated."""

