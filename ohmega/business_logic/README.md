#Business logic module

This directory contains several files that define the interface for your business logic - the actual goal of what your integration is meant to do. There are [intended] to be submodules for several types of common business logic goals:

* Providing callbacks to be executed on task changes
* Providing a method to "sync" with initial task state - that is, to check and maybe act on all tasks in a project

Future:

* To respond to team changes (i.e. a new team membership)
* To respond to changes in a project or tag, such as keeping up to date a "live" dashboard or report
