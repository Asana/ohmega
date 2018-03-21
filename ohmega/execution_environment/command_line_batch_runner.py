import logging
import os
import asana
from ohmega.business_logic.asana_callbacks import AsanaCallbacks
from ohmega.services.configuration_service import ConfigurationService


logger = logging.getLogger(__name__)


class CommandLineBatchRunner(object):
    """ The most basic runner - a runner that is called from a command line app
    in a way that's not necessarily meant to use events or webhooks. As with
    other runners, this is the top of the container of state, and will provide
    access between services to each other (so for instance it holds the logging
    service's state so that other services have access to it.) All runners take
    a top level scope for what they pay attention to; at this time, that is
    only a project.
    """

    def __init__(self, scope_project_id, configuration_project_id=None):
        self._project_id = scope_project_id
        if configuration_project_id is None:
            configuration_project_id = scope_project_id
        self._configuration_service = ConfigurationService(
                self, configuration_project_id)
        # TODO: this PAT setup is bogus, there should be a service that
        # provides this for us.
        self._client = asana.Client.access_token(
                os.environ['ASANA_PERSONAL_ACCESS_TOKEN'])
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
        return self._callback_manager.scan_project(self._project_id)
