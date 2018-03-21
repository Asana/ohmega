import asana

from . import db


# TODO: Make this flexible if we want to allow consumers to manage which events
# they care about.
class EventsManager(object):

    __TASK_FIELDS = [
        '(this|subtasks).id',
        '(this|subtasks).name',
        'memberships.(project|section).(id|name)',
        'subtasks.tags.(id|name)',
    ]

    def __init__(self, asana_client):
        self.asana_client = asana_client

    def _get_events(self, resource_id, sync_token):
        try:
            events_dict = self.asana_client.events.get(params={
                'resource': resource_id,
                'sync': sync_token
            })
            events = events_dict['data']
            db.save_sync_token(resource_id, events_dict['sync'])
        except asana.error.InvalidTokenError as e:
            db.save_sync_token(resource_id, e.sync)
            events = None

        return events

    def _filter_events_to_task_ids(self, events):
        """Filter a list of events to a set of relevant task IDs.

        Filter a list of events to a set of relevant task IDs to pull down
        information from the Asana API. This filters only "added" or "changed"
        task events and returns the unique set of task IDs associated with
        those events.

        :param list events: A list of event objects (dicts) returned from
            Asana's API.

        """
        # FIXME: Note that this explicitly only listens to task events - to my
        # knowledge assignment happens as a story, and may not trigger an
        # event, so we should look into whether we need to pull down story
        # events as well.
        return frozenset(
            e['resource']['id'] for e in events
            if e['type'] == 'task'
            and e['action'] in ('added', 'changed')
        )

    def _retrieve_tasks(
            self, resource_id, sync_token, resource_type='project'):
        events = self._get_events(resource_id, sync_token)
        full_refresh = events is None
        if not full_refresh and len(events) == 0:
            return []
        if resource_type == 'task':
            # Always grab the task, because we have at least one event or it's
            # a full refresh
            return [self.asana_client.tasks.find_by_id(
                resource_id, fields=self.__TASK_FIELDS)]
        elif resource_type == 'project':
            if full_refresh:
                # Grab all of the tasks
                return list(
                    self.asana_client.projects.tasks(
                        resource_id, fields=self.__TASK_FIELDS))
            else:
                task_ids = self._filter_events_to_task_ids(events)
                tasks = []
                for tid in task_ids:
                    try:
                        tasks.append(self.asana_client.tasks.find_by_id(
                            tid, fields=self.__TASK_FIELDS))
                    except asana.error.AsanaError:
                        # TODO: Log a warning here
                        continue
                return tasks

    def sync_resources(self, resources):
        resource_ids = [r['id'] for r in resources]
        sync_tokens = db.get_sync_tokens(resource_ids)
        resource_tasks = {}
        for resource in resources:
            resource_id = resource['id']
            try:
                tasks = self._retrieve_tasks(
                    resource_id, sync_tokens.get(resource_id),
                    resource['type'])
            except asana.error.AsanaError:
                # TODO: Log an error once we have logging setup.
                tasks = []
            resource_tasks[resource_id] = tasks

        return resource_tasks
