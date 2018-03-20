#!/usr/bin/env python

from __future__ import print_function

import argparse
import json
import sys

import asana

from ohmega import oauth

OAUTH_CLIENT_ID = 590240433767661
OAUTH_CLIENT_SECRET = '436cf06a88774feefd41cbc6c9251f45'


def printerr(msg):
    print(msg, file=sys.stderr)


def print_asana_error(msg, ex):
    printerr(
        'ERROR: {}\nStatus: {}\nMessage: {}'.format(
            msg, ex.status, ex.message))
    if ex.response is not None:
        printerr('\nJSON Response:')
        printerr(json.dumps(ex.response.json(), indent=2))


def parser():
    parser = argparse.ArgumentParser(
        description='Initializes OAuth Client for usage with Ohmega')
    parser.add_argument('client_id', type=int, help=(
        'The OAuth Client ID obtained from the Manage Developer Apps page '
        'in Asana.'
    ))
    parser.add_argument('client_secret', help=(
        'The OAuth Client Secret obtained from the Manage Developer Apps page '
        'in Asana.'
    ))

    return parser


def main():
    args = parser().parse_args()
    asana_client = oauth.asana_cli_oauth_client(
        (args.client_id, args.client_secret), reauth=True)
    try:
        me = asana_client.users.me()
        print(
            "You've successfully authenticated Ohmega!\n"
            'Name: {}\nUser ID: {}\nEmail: {}'.format(
                me['name'], me['id'], me['email']))
    except asana.error.NoAuthorizationError as ex:
        print_asana_error('Asana OAuth Client was not authorized!', ex)
    except asana.error.AsanaError as ex:
        print_asana_error(
            'An error occurred when testing OAuth client '
            'authorization!', ex)


if __name__ == '__main__':
    main()
