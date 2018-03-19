from abc import ABCMeta

#Apply logic to the tasks in a project.
# (For now, the tasks can only apply on a per-project basis)
class TaskLogic(Object):
    __metaclass__ = ABCMeta

    @classmethod
    def register(projectId)

    def __init__(self, projectId, client):
        self._projectId = projectId
        self._client = client

    def taskChangedTemplate(taskId):
        """Template method strategy for creating action for taskChanged"""
        #Assume for now that we can definitely get the event from an event stream
        oldTask = getStoredTask(taskId)
        nowTask = getCurrentTaskState(taskId)
        diff = calculateDiffForTasks(oldTask, nowTask)
        updatedTask = self.taskChanged(oldTask, diff, nowTask)
        diff = calculateDiffForTasks(nowTask, updatedTask)
        enactTaskDiff(nowTask, diff)

    @abstractmethod
    def taskChanged(oldTask, diff, nowTask):
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


    def taskScannedTemplate(taskId):
        """Template method strategy for creating action for taskScanned"""
        task = getCurrentTaskState(taskId)
        updatedTask = self.taskScanned(task)
        enactTaskDiff(task, diff)

        @abstractmethod
    def taskScanned(task):
        """Subclasses should implement this method in order to take action when a task is scanned
           There is no diff passed, because this method is called when there is no information
           about the previous state of a task.
        """

    def taskStagnantTemplate(taskId):
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
        
        cachedTask = getStoredTask(taskId)
        if self.isTaskStagnant(cachedTask):
            nowTask = getCurrentTaskState(taskId)
            if self.isTaskStagnant(nowTask):
                updatedTask = self.taskStagnant(task)
                diff = calculateDiffForTasks(nowTask, updatedTask)
                enactTaskDiff(updatedTask)

    @abstractmethod
    def isTaskStagnant(task):
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
    def taskStagnant(task):


    # TODO: This should be its own class or series of classes.
    # The ways in which a diff can be enacted are huge, and we want to be able to make
    # some simplifications or guesses.
    def enactTaskDiff(diff):
        # A pipeline that enacts changes that have to happen in sequence, for instance,
        # adding and removing memberships then removing that key from the diff; proceed.
        diff = self.enactMembershipsChangedDiff(diff)
        diff = self.enactFollowerAddedDiff(diff)

    def enactMembershipsChangedDiff(diff):
        # addMembership
        # remove the 
