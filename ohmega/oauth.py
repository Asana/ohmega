from __future__ import print_function

import asana

from . import db


OAUTH_CLI_REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


def asana_cli_oauth_client(client_id, client_secret):
    token = db.get_oauth_token()
    if token:
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
        client = asana.Client.oauth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=OAUTH_CLI_REDIRECT_URI)

        url, state = client.session.authorization_url()

        print(
            'Please access the following URL in a web browser and '
            'paste in your code below:\n{}'.format(url))
        code = raw_input('--> ')

        token = client.session.fetch_token(code=code)
        db.save_oauth_token(token)

    return client
