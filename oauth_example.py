import json
import os.path

import asana


OAUTH_CLIENT_ID = 590240433767661
OAUTH_TOKEN_FNAME = 'oauth_token.json'
OAUTH_REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


def cli_oauth_client(client_secret):
    token = get_oauth_token()
    if token:
        refresh_kwargs = {
            'client_id': OAUTH_CLIENT_ID,
            'client_secret': client_secret,
            'redirect_uri': OAUTH_REDIRECT_URI
        }
        client = asana.Client.oauth(
            client_id=OAUTH_CLIENT_ID,
            token=token,
            auto_refresh_url=asana.session.AsanaOAuth2Session.token_url,
            auto_refresh_kwargs=refresh_kwargs,
            token_updater=save_oauth_token)
    else:
        client = asana.Client.oauth(
            client_id=OAUTH_CLIENT_ID,
            client_secret=client_secret,
            redirect_uri=OAUTH_REDIRECT_URI)

        url, state = client.session.authorization_url()

        print(
            'Please access the following URL in a web browser and '
            'paste in your code below:\n{}'.format(url))
        code = input('--> ')

        token = client.session.fetch_token(code=code)
        save_oauth_token(token)

    return client


def get_oauth_token():
    token = None
    if os.path.exists('oauth_token.json'):
        with open(OAUTH_TOKEN_FNAME) as fobj:
            token = json.load(fobj)

    return token


def save_oauth_token(token):
    with open(OAUTH_TOKEN_FNAME, 'w') as fobj:
        json.dump(token, fobj, indent=2)
