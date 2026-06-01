This file contains the code for running an "LLM Instance"

This is the server that actually runs the LLM, either on the same machine as the HTTP server or (more likely) 
a separate device. It does not communicate directly with the client (i.e. user).

It does not currently support performing LLM inference for multiple prompts asynchronously on the same device.
Mainly because I haven't been able to test such functionality due to the limited resources available to me, but
I do plan on adding this at a later date.