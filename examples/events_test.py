import logging
import logging.config
import json

import yaml

from ohmega import oauth, events


def init_logging():
    with open('../logging.yaml') as fobj:
        logging.config.dictConfig(yaml.load(fobj))


def main():
    init_logging()
    asana_client = oauth.asana_cli_oauth_client()
    events_mgr = events.EventsManager(asana_client)

    resources = events_mgr.sync_resources([
        {'id': 537972519778707, 'type': 'project'},
        {'id': 601743188547449, 'type': 'task'}
    ])

    with open('resources_test.json', 'w') as fobj:
        json.dump(resources, fobj)


if __name__ == '__main__':
    main()
