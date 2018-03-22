#!/usr/bin/env python
import logging
import logging.config
import sys
import os
import yaml
# This is only to run Ohmega from the local dir.
# It is meant to be installed from the Python package, but
# we do this so you can try locally without installing.
sys.path.append(os.path.abspath("../"))

# We show here how the configuration for the app lives inside Asana and is read
# when the script is run.
# This will be a command line app that runs once and exits
from ohmega.execution_environment.command_line_batch_runner \
    import CommandLineBatchRunner


with open('../logging.yaml') as fobj:
    logging.config.dictConfig(yaml.load(fobj))

# This is the project that this script will run against.
# If there isn't a second ID for a separate project that contains the Asana
# configuration,
# we look in the same project for the config task.
project_id = 157953484489631
runner = CommandLineBatchRunner(project_id)
# Print the configuration (a Python dictionary)
print(runner.configuration.read_config_from_asana())
