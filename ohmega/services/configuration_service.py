
# The configuration service manages the script configuration and is the basic way for the script to initialize its state.
# * It starts with going to a particular project in Asana
# * The project is then looked for for a configuration task. (*How?* All I can think of is an O(n) scan of the project, or of a tag for all such configuration tasks (but which is more opaque and error-prone)... I think the best we can do is to do the O(n) scan and save the task ID in our storage for future reference. Even though we'll likely want to refresh the config every run, we want to save the most recent config offline in order to restore if someone deletes the task.)
# * If none is found, a task will be created with the default configuration (or maybe a cached one from a previous run) and a completed subtask assigned to the project owner (so basically effectively just and Inbox message) to inform them that the workflow has been bootstrapped, and reminds them that the configuration task should not be deleted. (Do we later delete these tasks to keep them from accumulating?)
# * The configuration is then read from the configuration task into a tree structure.
# * The configuration is compared to the default tree and overlaid/validated for keys. If the validation fails, the project owner (and maybe followed by the app authorizer) get an incomplete task telling them that there is a non-recoverable difference in config between Asana's configuration state and the in-script default config.

# Command line switches are honored. These take a command line argument, map it to a JSON path, map the command line key to a json key, and apply it to the config

# The config is now set.

# XCXC: from ohmega.services import ConfigStorageService

import yaml

class ConfigurationService(object):
    
    def __init__(self, runner, project_id):
        self._runner = runner
        self._project_id = project_id

    def read_config_from_asana(self):
        config_task = self.find_config_task()
        config = self.read_config_from_task_or_subtask(config_task)
        return config


        # TODO: do we want to implement a way to restore this tag as well? That is, on first startup with no
        # config storage datastore, do we want to look for tasks like this by name only, and when we find one,
        # infer that its tag is the config tag?
    def find_config_task(self):
        #XCXC if not self._storage_service.config_task_id_for_project(self._project_id):
        for task in self._runner.client.tasks.find_by_project(self._project_id, fields="name,tags,tags.name"):
            self._runner.log.debug("Investigating for config: %d", task[u'id'])
            for tag in task[u'tags']:
                if tag[u'id'] == 599494283563095:
                    self._runner.log.debug("Matched %d via tag", task[u'id'])
                    # Fix the name if it doesn't match
                    if task[u'name'] != u'Ohmega Automation Configuration':
                        self._runner.client.tasks.update(task[u'id'], { u'name': 'Ohmega Automation Configuration'})
                    self._runner.log.info("Config task found: %d", task[u'id'])
                    return task

    def read_config_from_task_or_subtask(self, task):
        """Recursively descend through subtasks to build a Python config structure"""
        config_object = dict()
        for subtask in self._runner.client.tasks.subtasks(task[u'id']):
            config = yaml.load(subtask[u'name'])
            config_object[config.keys()[0]] = config.values()[0]
        return config_object
