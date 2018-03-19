# Services


Services are abstracted functionality that can be used to fulfill certain actions in an abstract and pre-simplified way. For instance, there is a logging service that knows how to set up a good default logging configuration for each different runner (so that, for instance, a command line runner by default asks the logging service to set up a logger for printing to the command line, whereas a http runner might ask for a rotating log file.)

In addition, services can be used to perform Asana queries or to programmatically look up certain things in a simplified, abstract way. Think of them as something like a simplified object relational model that knows how to interact with both a database and the Asana API, which means we can use locally stored data as much as possible while still having the ability to ask Asana for updated data. This is useful for, say, User resources that don't change very often.

(Note: It's recommended to install a cache warming business logic module that runs nightly [link to example] even in these cases, since it can make scripts simpler to understand when the data is at least somewhat up to date - imagine a user changing their name, for instance).

