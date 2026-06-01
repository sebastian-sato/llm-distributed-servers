This is the code for the HTTP server that the client will actually connect to, 
it acts as a middle man between the clients and one or more LLM instances they might want to access.

It includes functionality for simple load balancing and asynchronous, non blocking usage. 
In a real commercial setting you would probably instead want to use dedicated software for this task, like NGINX. 
However, I wanted to practice writing something like this on my own.

It also includes basic support for authentication, so you can control who can access your models.

Note that authentication as it is currently implemented here is basic, and is done using a simple plain-text password.
So in practice you'd want to get a webdomain and SSL certificate for your HTTP server as well, 
or implement your own authentication system that's more robust and isn't vulnerable to snooping.
