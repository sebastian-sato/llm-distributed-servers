# LLM Distributed Servers
An improved version of my simple LLM HTTP Server that features simple password authentication and
allows for requests to be distributed across multiple servers for improved performance. It is still
a work in progress and some features, such as reliable asynchronous inference on a single LLM instance,
have yet to be implemented.

**Dependencies:**
```
pip3 install uvicorn fastapi
```
Plus whatever your LLM pipeline depends on for the LLM instance.

**Usage:**

For the HTTP server and LLM instance, simply run server.py

In the HTTP server, make sure to add information for the LLM instances in INSTANCES.json.

You'll also probably want to replace their shared token with something more scure (The shared token
is what the HTTP server and LLM instances use to verify their connection).

And you'll want to set a different password, you can do so using setpassword.py in the HTTP server directory.
This is the password that the client will use to access the intermediate HTTP server.
