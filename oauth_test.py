from __future__ import print_function

import json

from ohmega import oauth

OAUTH_CLIENT_ID = 590240433767661
OAUTH_CLIENT_SECRET = '436cf06a88774feefd41cbc6c9251f45'

if __name__ == '__main__':
    client = oauth.asana_cli_oauth_client(OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET)
    print(json.dumps(client.users.me(), indent=2))
