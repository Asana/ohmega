import logging
import os
import asana
from ohmega.business_logic.project_scanner import ProjectScanner
from ohmega.business_logic.tag_scanner import TagScanner
from ohmega.services.configuration_service import ConfigurationService
from . import oauth


logger = logging.getLogger(__name__)


class CommandLineBatchRunner(object): 
    """ The most basic runner - a runner that is called from a command line app
    in a way that's not necessarily meant to use events or webhooks. As with
    other runners, this is the top of the container of state.
    """

    def __init__(self, app_config_filename, configuration_task_id, workflow_name):
        self._app_config_filename = app_config_filename
        self._configuration_task_id = configuration_task_id
        self._workflow_name = workflow_name
        self._configuration_service = ConfigurationService(
                self, configuration_task_id)
        self._client = oauth.asana_cli_oauth_client(app_config_filename)
        self._project_scanner = ProjectScanner(self.client)
        self._tag_scanner = TagScanner(self.client)

    @property
    def client(self):
        return self._client

    def include_project_scan_operation(self, callback):
        """ Delegate a callback to be executed by the project scanner.
        """
        self._project_scanner.include_project_scan_operation(callback)

    def include_tag_scan_operation(self, callback):
        """ Delegate a callback to be executed by the tag scanner.
        """
        self._tag_scanner.include_tag_scan_operation(callback)



    def run(self):
        # First, use the configuration service to load config from Asana
        config = self._configuration_service.config()
        # Do the project scan phase
        self._project_scanner.load_config(config)
        self._project_scanner.execute_project_scans()
        # Do the tag scans
        self._tag_scanner.load_config(config)
        self._tag_scanner.execute_tag_scans()
        # Other runners might have other execution mode, like watching a project for changes,
        # but this runner doesn't do that.
