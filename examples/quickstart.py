#!/usr/bin/env python

import sys
import os
# This is only to run Ohmega from the local dir.
# It is meant to be installed from the Python package, but
# we do this so you can try locally without installing.
sys.path.append(os.path.abspath("../"))

from ohmega.execution_environment.command_line_batch_runner import CommandLineBatchRunner

# Define a callback
def log_on_task_scanned(task, client):
    runner.log.info("Task scanned: {} {}".format(task[u'id'], task[u'name']))

# Spoof config, which is normally read from a known Asana location.
# TODO: we don't want the Asana-read config to be able to change the project.
# We should have some sort of way to pin this to only the right one.
configuration = {}
configuration['project'] = 157953484489631

runner = CommandLineBatchRunner(configuration)
callback_manager = runner.callback_manager
callback_manager.register_task_scanned_callback(log_on_task_scanned)
runner.run()

