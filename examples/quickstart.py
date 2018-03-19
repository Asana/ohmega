#!/usr/bin/env python

import sys
import os

# This is only to run Ohmega from the local dir.
# It is meant to be installed from the Python package, but
# we do this so you can try locally without installing.
sys.path.append(os.path.abspath("../"))

from ohmega.services.logging_service import LoggingService, BasicLoggingConfiguration

ls = LoggingService(BasicLoggingConfiguration.COMMAND_LINE_DEBUG)

ls.logger.info("HAI")


