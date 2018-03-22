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
def print_task(task, client, config):
    print("Task scanned: {} {}".format(task[u'id'], task[u'name'].encode("utf-8")))


# Set up a command line runner
runner = CommandLineBatchRunner("credentials.yaml", 599494283563094, "Quick Start")
# Enable this operation for being able to be included in the configuration.
# This enables a config block named this function name which can then be used
# to set up the scan.
runner.include_project_scan_operation(print_task)
# Run it!
runner.run()
