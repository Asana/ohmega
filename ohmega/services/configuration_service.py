# The configuration service manages the script configuration and is the basic
# way for the script to initialize its state.
# * It starts with going to a particular task in Asana. This task is the root
# of the configuration tree and is looked for to bootstrap the app.
# * The project is then looked for for a configuration task. (*How#
# * If none is found, a task will be created with the default configuration (or
# maybe a cached one from a previous run) and a task with a link assigned to
# the project owner (so basically effectively just an Inbox message) to inform
# them that the workflow has been bootstrapped and the task should be filed
# in some appropriate place.
# * The configuration is then read from the configuration task into a tree
# structure.
# * The configuration is compared to the default tree and overlaid/validated
# for keys. If the validation fails, the project owner (and maybe followed by
# the app authorizer) get an incomplete task telling them that there is a
# non-recoverable difference in config between Asana's configuration state and
# the in-script default config.
# * Command line switches are honored. These take a command line argument, map
# it to a JSON path, map the command line key to a json key, and apply it to
# the config.

# The config is now set.
import os
import datetime
import logging
import sys
import traceback
import yaml
from collections import OrderedDict

logger = logging.getLogger(__name__)


def represent_odict(dump, tag, mapping, flow_style=None):
    """Taken from https://gist.github.com/miracle2k/3184458
    OrderedDict doesn't get dumped by default, but we want to
    preserve the order, so we have to add another representer
    to PyYAML to achieve this.
    """
    value = []
    node = yaml.MappingNode(tag, value, flow_style=flow_style)
    if dump.alias_key is not None:
        dump.represented_objects[dump.alias_key] = node
    best_style = True
    if hasattr(mapping, 'items'):
        mapping = mapping.items()
    for item_key, item_value in mapping:
        node_key = dump.represent_data(item_key)
        node_value = dump.represent_data(item_value)
        if not (isinstance(node_key, yaml.ScalarNode) and not node_key.style):
            best_style = False
        if not (isinstance(node_value, yaml.ScalarNode) and not node_value.style):
            best_style = False
        value.append((node_key, node_value))
    if flow_style is None:
        if dump.default_flow_style is not None:
            node.flow_style = dump.default_flow_style
        else:
            node.flow_style = best_style
    return node

yaml.SafeDumper.add_representer(OrderedDict,
    lambda dumper, value: represent_odict(dumper, u'tag:yaml.org,2002:map', value))


class ConfigurationService(object):
    """Class to manage reading from and writing to the configuration task in Asana.
    """

    def __init__(self, runner, config_task_id):
        self._runner = runner
        self._config_task_id = config_task_id
        self._config_task = None
        self._config = None
        self._ohmega_version = os.popen("git rev-parse HEAD").read().strip()

    def config(self):
        return self.read_config_from_asana()

    def read_config_from_asana(self):
        try:
            self._config_task = self._get_config_task_from_asana()
            if not self._config_task:
                logger.warn("Could not get configuration task from Asana with id %s",
                            self._config_task_id)
            self._config = self._read_config_from_task(self._config_task)
            self._update_config_task_description()
            logger.info("Successfully parsed configuration")
            logger.debug(yaml.safe_dump(self._config))
            return self._config
        except Exception as ex:
            logger.warn("Failed to parse configuration: %s",
                        traceback.format_tb(sys.exc_info()[2]))
            self._update_config_task_description(ex)
            return None

    def _get_config_task_from_asana(self):
        return self._runner.client.tasks.find_by_id(self._config_task_id)

    def _update_config_task_description(self, exception=None):

        if exception is None:
            exception_string = "None"
        else:
            exception_string = traceback.format_tb(sys.exc_info()[2])
        template = """Last run: {datetime}
Any exception? {exception}
Git revision: {revision}
Configuration:
{config}"""
        report = template.format(
                datetime=datetime.datetime.now().isoformat(),
                revision = self._ohmega_version,
                exception=exception_string,
                config=yaml.safe_dump(
                    self._config,
                    default_flow_style=False))
        self._runner.client.tasks.update(
                self._config_task[u'gid'],
                notes=report)

    def _read_config_from_task(self, task):
        """Recursively descend through subtasks to build a Python config
        structure. This does not use expand, but issues a request per
        task.
        """
        config_object = OrderedDict()
        for subtask in self._runner.client.tasks.subtasks(
                task[u'gid'],
                fields="name,notes,subtasks,completed"):
            if subtask[u'completed'] == True:
                logger.info("Task %s is completed (deactivated); omitting from config",
                        subtask[u'name'])
                continue
            config = yaml.load(subtask[u'name'])
            # If a config is of type "dict", infer it's a leaf node.
            if type(config) is dict:
                key = config.keys()[0]
                value = config.values()[0]
                config_object[key] = value
            # If a config is of type "string"
            if type(config) is str:
                key = config
                # If it has no subtasks, it's a leaf and the value is
                # the description of the task.
                if len(subtask[u'subtasks']) == 0:
                    value = yaml.load(subtask[u'notes'])
                    config_object[key] = value
                else:
                    # Recurse
                    sub_config = self._read_config_from_task(subtask)
                    config_object[key] = sub_config
        return config_object
