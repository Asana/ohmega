import os
import asana
from ohmega.business_logic.asana_callbacks import AsanaCallbacks
from ohmega.services.logging_service import LoggingService, BasicLoggingConfiguration

class CommandLineBatchRunner(object):

    # A client can be passed in if this script is to be run in a non-default manner.
    def __init__(self, configuration):

        self._conf = configuration
        self._client = None
        self._callback_manager = None
        self._ls = LoggingService(BasicLoggingConfiguration.COMMAND_LINE)

    #TODO: this is bogus, there should be a service that provides this for us.
    def client(self):
        if not self._client:
            self._client = asana.Client.access_token(os.environ['ASANA_PERSONAL_ACCESS_TOKEN'])
        return self._client

    @property
    def callback_manager(self):
        if not self._callback_manager:
            self._callback_manager = AsanaCallbacks(self.client())
        return self._callback_manager

    @property
    def log(self):
        return self._ls.logger

    def run(self):
        return self._callback_manager.scan_project(self._conf['project'])
        

