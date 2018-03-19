#!/usr/bin/env python

import sys
import os
import asana
# This is only to run Ohmega from the local dir.
# It is meant to be installed from the Python package, but
# we do this so you can try locally without installing.
sys.path.append(os.path.abspath("../"))

from ohmega.services.logging_service import LoggingService, BasicLoggingConfiguration
from ohmega.business_logic.asana_callbacks import AsanaCallbacks

ls = LoggingService(BasicLoggingConfiguration.COMMAND_LINE)
ls.logger.info("Hello, world!")

# This should be done under the hood by delegating to something that knows how to get creds. Ignore for now.
_client = asana.Client.access_token(os.environ['ASANA_PERSONAL_ACCESS_TOKEN'])
############

callback_manager = AsanaCallbacks(_client)

# Define a callback
def log_on_task_scanned(task, client):
    ls.logger.info(task)


callback_manager.register_task_scanned_callback(log_on_task_scanned)

callback_manager.scan_project(157953484489631)
