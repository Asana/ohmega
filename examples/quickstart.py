#!/usr/bin/env python
import sys
import os
from ohmega.execution_environment.command_line_batch_runner\
    import CommandLineBatchRunner

# This is only to set the path relative to the current file for
# testing before installing Ohmega.
sys.path.append(os.path.abspath("../"))


# Define a callback
def log_on_task_scanned(task, client):
    runner.log.info("Task scanned: {} {}".format(task[u'id'], task[u'name']))


# Spoof config, which is normally read from a known Asana location.
# TODO: we don't want the Asana-read config to be able to change the project.
# We should have some sort of way to pin this to only the right one.

runner = CommandLineBatchRunner(157953484489631)
callback_manager = runner.callback_manager
callback_manager.register_task_scanned_callback(log_on_task_scanned)
runner.run()
