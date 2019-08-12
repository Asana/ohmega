# Execution environment module

The logic around the Ohmega framework is intended to operate consistently in several different execution environments. These different environments are intended to be built in a module in this directory such that the specifics of running in a different environment are abstracted away from the rest of the framework, and appear just as a generic "environment" to the rest of the app. These specifics might include the lifetime of the app, how to manage and operate on periodic cycles, what logging to set up, how changes in Asana might be represented, and so on.

For example, some of these environments could include:
* Calling a script written from a command line in a non-blocking and "batch operation" way
* Calling a script written from a command line that is meant to regularly be executed with a `cron` job
* Calling a script that lives in a Mac bundle so that non-technical folks can more easily run it
* Building a webserver that can react to webhooks and respond to them (waits for incoming network activity)
* A containerized app that runs on e.g. Heroku
* A serverless app that runs on e.g. Amazon Lambda
