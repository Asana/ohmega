#!/usr/bin/env python
import logging
import logging.config
import sys
import os
import yaml
from ohmega.execution_environment.command_line_batch_runner\
    import CommandLineBatchRunner

# This is only to set the path relative to the current file for
# testing before installing Ohmega.
sys.path.append(os.path.abspath("../"))


with open('../logging.yaml') as fobj:
    logging.config.dictConfig(yaml.load(fobj))


# Define a callback
def print_on_task_scanned(task, client):
    print("Task scanned: {} {}".format(task[u'id'], task[u'name']))


# Set up a command line runner
runner = CommandLineBatchRunner(157953484489631)
# Get the callback manager from the runner
callback_manager = runner.callback_manager
# Register our callback
callback_manager.register_task_scanned_callback(print_on_task_scanned)
# Run it!
runner.run()
