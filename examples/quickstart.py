#!/usr/bin/env python

import sys
import os
import asana
# This is only to run Ohmega from the local dir.
# It is meant to be installed from the Python package, but
# we do this so you can try locally without installing.
sys.path.append(os.path.abspath("../"))

from ohmega.services.logging_service import LoggingService, BasicLoggingConfiguration
from ohmega.services.configuration_service import ConfigurationService
#from ohmega.business_logic.task_logic import TaskLogic

ls = LoggingService(BasicLoggingConfiguration.COMMAND_LINE)
ls.logger.info("HAI")

# This should be done under the hood by delegating to something that knows how to get creds. Ignore for now.
_client = asana.Client.access_token(os.environ['ASANA_PERSONAL_ACCESS_TOKEN'])
cs = ConfigurationService(_client, 157953484489631)
############

config = cs.read_config_from_asana()
ls.logger.info(config)

# Based on the config, do some business logic.

#class DoSomethingUseful(object):
#    def task_scanned(now_task):
#        ls.logger.info(task)

#TaskLogic.register(DoSomethingUseful)
