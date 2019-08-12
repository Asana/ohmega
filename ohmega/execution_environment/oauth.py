from __future__ import print_function

from abc import ABCMeta, abstractmethod
import logging
import os.path

import asana
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
import six
from six.moves import input
import yaml

from ohmega.services import db
from .errors import AsanaAuthError, ConfigError


logger = logging.getLogger(__name__)


OAUTH_CLI_REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


# TODO: This is a bit clunky for just YAML handling, but is mostly proof of
# concept for supporting other secret/config systems.
@six.add_metaclass(ABCMeta)
class AppInfoConfig(object):

    @classmethod
    @abstractmethod
    def get_app_info(cls):
        pass

    @classmethod
    @abstractmethod
    def store_app_info(cls, client_id, client_secret):
        pass


class YamlAppInfoConfig(AppInfoConfig):

    __APP_INFO_KEYS = ('client_id', 'client_secret')

    @classmethod
    def get_app_info(cls, app_info_file):
        logger.debug('Retrieving OAuth2 App Info from {}'.format(
            app_info_file))
        if os.path.exists(app_info_file):
            with open(app_info_file) as fobj:
                app_info_dict = yaml.load(fobj)
            if any(key not in app_info_dict for key in cls.__APP_INFO_KEYS):
                raise ConfigError(
                    '{} is missing one of the OAuth2 app info '
                    'keys: {}'.format(cls.__APP_INFO_KEYS))
            return (app_info_dict['client_id'], app_info_dict['client_secret'])
        else:
            logger.warn("""No file found at \"%s\".Please supply the path to 
a YAML file with Asana OAuth app credentials""", app_info_file)
            exit(-1)
            return (None, None)

    @classmethod
    def store_app_info(cls, app_info_file, client_id, client_secret):
        logger.debug(
            'Storing OAuth2 App Info to {}'.format(app_info_file))
        app_info_dict = {
            'client_id': client_id,
            'client_secret': client_secret
        }
        with open(app_info_file, 'w') as fobj:
            yaml.dump(app_info_dict, fobj, default_flow_style=False)


def asana_cli_oauth_client(app_info_file=None, reauth=False):
    """Instantiate a new Asana OAuth2 client.

    :param tuple app_info: The (client_id, client_secret) tuple for the Asana
        OAuth2 app.
    :param bool reauth: If True, purge any cached access tokens and
        reauthorizes the app for the user.
    :return: An OAuth2 authenticated Asana API client.

    """

    if not app_info_file:
        logger.error("Please supply the name of a YAML file for getting app credentials")
        exit(-1)
    else:
        client_id, client_secret = YamlAppInfoConfig.get_app_info(app_info_file)
    if None in (client_id, client_secret):
        logger.warn("One of the needed OAuth app credentials was missing")
        raise ValueError(
            'client_id or client_secret was not specified')

    if reauth:
        logger.debug('Reauthenticating OAuth2 client.')
        token = None
    else:
        token = db.get_oauth_token()

    if token:
        logger.debug('Token exists in database, using in new client.')
        refresh_kwargs = {
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': OAUTH_CLI_REDIRECT_URI
        }
        client = asana.Client.oauth(
            client_id=client_id,
            token=token,
            auto_refresh_url=asana.session.AsanaOAuth2Session.token_url,
            auto_refresh_kwargs=refresh_kwargs,
            token_updater=db.save_oauth_token)
    else:
        logger.debug(
            "Token doesn't currently exist, running through entire auth flow")
        client = asana.Client.oauth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=OAUTH_CLI_REDIRECT_URI)

        url, state = client.session.authorization_url()

        print(
            'Please access the following URL in a web browser and '
            'paste in your code below:\n{}'.format(url))
        code = input('Code --> ')
        print()

        try:
            token = client.session.fetch_token(code=code)
        except OAuth2Error as ex:
            six.raise_from(
                AsanaAuthError(
                    'An error occured when attempting to fetch '
                    'an OAuth token.'), ex)
        except ValueError as ex:
            six.raise_from(
                AsanaAuthError(
                    'Code was not supplied for OAuth token exchange - did you '
                    'forget to paste the code you received from Asana?'),
                ex)
        db.save_oauth_token(token)
        YamlAppInfoConfig.store_app_info(app_info_file, client_id, client_secret)

    return client
