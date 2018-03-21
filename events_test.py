import json

from ohmega import oauth, events


def main():
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
