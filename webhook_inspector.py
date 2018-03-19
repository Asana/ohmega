#!/usr/bin/env python

import asana, sys, os, json, logging, signal, threading
from asana.error import AsanaError
from dateutil import parser

from dateutil import parser
from flask import Flask, request, make_response

"""
Procedure for using this script to log live webhooks:

* Create a new PAT - we're going to use ngrok on prod Asana, and don't want to give it long-term middleman access
  * https://app.asana.com/-/account_api
* Set this PAT in the environment variable TEMP_PAT
  * export TEMP_PAT=[pat]
* Run `ngrok http 8090`
* Copy the subdomain, e.g. e91dadc7
* Run this script with these positional args:
  * First arg: ngrok subdomain
  * Second arg: ngrok port (e.g. 8090)
* Visit localhost:8090/create_hook to create the hook
* Follow the returned link to see your webhook.
* Make changes in Asana and see the logs from the returned webhooks.

* Don't forget to deauthorize your temp PAT when you're done.
"""



secret = None
if 'TEMP_PAT' in os.environ:
    secret = os.environ['TEMP_PAT']
else:
        print "No value for TEMP_PAT in env" and quit

project = None
if 'ASANA_SANDBOX_PROJECT' in os.environ:
    project = os.environ['ASANA_SANDBOX_PROJECT'] 
else:
    print "No value for ASANA_SANDBOX_PROJECT in env" and quit

client = asana.Client.access_token(secret)

app = Flask('Webhook inspector')
app.logger.setLevel(logging.INFO)

ngrok_subdomain = sys.argv[1]


@app.route("/ping", methods=["GET"])
def ping():
    return "Pong"

webhook = None

class CreateWebhookThread(threading.Thread):
    def run(self):
        global webhook
        webhook = client.webhooks.create(resource=project, target="https://{0}.ngrok.io/receive-webhook/0".format(ngrok_subdomain))

create_thread = CreateWebhookThread()


@app.route("/create_hook", methods=["GET"])
def create_hook():
    global webhook
    global create_thread
    if webhook is not None:
        return "Hook already created: " + str(webhook)
# Should guard webhook variable. Ah well.
    create_thread.start()
    return "Creating hook. Call <a href=/webhook>/webhook</a> to inspect."

@app.route("/webhook", methods=["GET"])
def get_webhook():
    global webhook
    return str(webhook)

@app.route("/remove_hook", methods=["GET"])
def teardown():
    global webhook
    if webhook is None:
        return "No webhook"
    retries = 5
    while retries > 0:
        try:
            client.webhooks.delete_by_id(webhook[u"id"])
            webhook = None
            return "Deleted"
        except AsanaError as e:
            print "Caught error: " + str(e)
            print "Retries " + str(retries)
    return ":( Not deleted :("


@app.route("/receive-webhook/<int:project_id>/<int:section_id>", methods=["POST"])
def receive_webhook_with_section(project_id, section_id):
    app.logger.info("Headers: " + str(request.headers));
    app.logger.info("BodyL: " + str(request.data));
    if "X-Hook-Secret" in request.headers:
        # Always accept :)
        app.logger.info("New webhook %s %s", project_id, section_id)
        response = make_response("", 200)
        response.headers["X-Hook-Secret"] = request.headers["X-Hook-Secret"]
        return response
    elif "X-Hook-Signature" in request.headers:
        # Never verify signature :/
        contents = json.loads(request.data)
        seen = set()
        app.logger.info("Received payload of size %s", len(contents["events"]))
        print contents
        return ""
    else:
        raise KeyError

@app.route("/receive-webhook/<int:project_id>", methods=["POST"])
def receive_webhook(project_id):
    return receive_webhook_with_section(project_id, None)

app.logger.addHandler(logging.StreamHandler())

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    teardown()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

app.run(port=int(sys.argv[2]), debug=True)

