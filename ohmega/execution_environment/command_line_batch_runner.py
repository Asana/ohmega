import logging
import os
import asana
from ohmega.business_logic.asana_callbacks import AsanaCallbacks
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
        self._callback_manager = AsanaCallbacks(self.client)

    @property
    def client(self):
        return self._client

    @property
    def callback_manager(self):
        return self._callback_manager

    @property
    def configuration(self):
        return self._configuration_service

    def run(self):
        # First, give the current configuration to the callbacks manager
        self._callback_manager.load_config(self.configuration.config())
        self._callback_manager.execute_project_scan()
