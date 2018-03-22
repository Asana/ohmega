#!/usr/bin/env python
import logging
import logging.config
import sys
import os
import yaml
# This is only to set the path relative to the current file for
# testing before installing Ohmega.
sys.path.append(os.path.abspath("../"))


from ohmega.execution_environment.command_line_batch_runner\
    import CommandLineBatchRunner


with open('../logging.yaml') as fobj:
    logging.config.dictConfig(yaml.load(fobj))


# Define a callback
def print_task(task, client):
    print("Task scanned: {} {}".format(task[u'id'], task[u'name']))


# Set up a command line runner
runner = CommandLineBatchRunner("credentials.yaml", 599494283563094, "Quick Start")
# Get the callback manager from the runner
callback_manager = runner.callback_manager
# Register our callback. A "project scan" means that based on the "Project Scans"
# key in our configuration we'll run this named callback for each.
callback_manager.on_project_scan(print_task)
# Run it!
runner.run()
