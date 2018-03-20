# Ohmega
The Asana Ohmega process automation toolkit

![Ohmega logo](ohmega_logo.png)

# What is Ohmega?

When it comes to process automation, there is a big gap between what it takes to create a good, reliable, performant method of automation and the actual task at hand. Often the desired business logic is along the lines of "When this happens, I want something else to happen", but getting software to do that set up can involve anything up to getting a publicly-addressible DNS-findable computer on the internet so we can deliver real-time webhooks. On top of that, figuring out *what*, exactly, has changed is another layer of work that can be challenging to really get right.

Ohmega is designed to be able to isolate the simple business logic from these steps through these goals:

* Business logic should be as simple as possible to implement. It should be easy to *understand* how to build something and get it built with a minimum of headaches
* Most of the gotchas around things like rate limits, cyclical logic, event deduplication should happen in an automatic and standardized fashion.
* Where the script is run should be minimally important to the business logic. The business logic should be, insofar as possible, the same whether it's run locally from a double-clickable app, a command line, a cron job, or in the cloud on (say) Heroku.
* The business logic should be as technically simple to implement as possible while remaining flexible. There should be no abstraction layer so deep as to be impenetrable.
* People who did not actually *write* the business logic should be empowered to adjust configuration and get information about what actions the business logic undertook.

This is what Ohmega is designed to do: to provide an environment that allows a "When this happens, do this" style of execution that is easy to implement on top of with very little in-depth engineering required.

# Where to start learning about Ohmega

# The examples directory provide some basic use cases built with Ohmega if you want to get up to speed quickly.

# Implementation details

Ohmega is designed to be tested against an actual, running instance of Asana in order to get perfect end-to-end behavior for the entire system. To that end, the #TODO automated tests will be run on commit against a sandbox environment that Asana maintains.

Data that is needed by Ohmega will be stored in a sqlite database. This database has either-there-and-not-corrupt-or-not-there semantics, and if it is deleted or gets corrupted on disk, a full scan (as if run for the first time) will be performed.

When diffs are possible, we use jsondiff

This will only work on a per-project configuration for 10,000 tasks. It will shut down and let the project or app maintainer know that they've got to do something to clear things up.
