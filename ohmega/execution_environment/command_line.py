
# The command line runner has these characteristics:

# It will first try to get authentication credentials from the environment (in case it's somehow being scripted).
# If this fails, it will check the database (which is where we think it would most be used)
# If this fails, it will spin up a Flask server (todo: that's overkill) on localhost:4878 (which is telephone numbers of "guru") in order to get an oauth redirect. The user will be sent to an Asana oauth page to get the credentials. These will be used in the refresh cycle and the relevant tokens stored in the database.


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
        

