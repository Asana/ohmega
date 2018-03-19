
# The command line runner has these characteristics:

# It will first try to get authentication credentials from the environment (in case it's somehow being scripted).
# If this fails, it will check the database (which is where we think it would most be used)
# If this fails, it will spin up a Flask server (todo: that's overkill) on localhost:4878 (which is telephone numbers of "guru") in order to get an oauth redirect. The user will be sent to an Asana oauth page to get the credentials. These will be used in the refresh cycle and the relevant tokens stored in the database.
# The relevant projects to be applied to are then looked for for configuration. If none is found, a task will be created with the default configuration (or maybe a cached one from a previous run; it should be clear from the message) and a subtask issed to the project owner to ask if this should be activated (bootstrapped) and reminding them that the configuration task should not be deleted.
# The configuration is then read from the configuration task.
# The default diff is compared to the configuration and overlaid/validated for keys. If the validation fails, both the project owner (and followed by the app authorizer) get a task telling them that there is a non-recoverable difference in config between live and default.
# Command line switches are honored. These take a command line argument, map it to a JSON path, map the command line key to a json key, and apply it to the config

# The config is now set.

# At this time, an attempt to run task logic against events in the project are started. If the events can't be fetched, a full scan is undertaken and the event is saved. (Should we provide a configuration param to only do scan?)

import os

class CommandLineRunner(Object):

    # A client can be passed in if this script is to be run in a non-default manner.
    def __init__(self, configuration_dict, client = None):
        self.conf_dict = configuration_dict
        self._client = client if client not None else self._client = CommandLineRunner.construct_client()

    @classmethod
    def construct_client(klass):
        # See if there are credentials in the environment. This allows for credentials to be,
        # for instance, a Personal Access Token (otherwise the model to be followed is that
        # the credentials are a user authorizing an OAuth app with creds in the DB.
        

