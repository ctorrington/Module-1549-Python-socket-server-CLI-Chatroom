# Module-1549-Python-socket-server-CLI-Chatroom

This is uploaded for posterity.

2nd year university project.

The specification was to create a cli chatroom that can be accessed remotely by users & run on a central server.

We chose to use python sockets to connect the users to the server.
Both the server & users are capable of sending & receiving data through the data_transfer module. 
The data is transmitted through the socket after being formatted into a dictionary & serialised.
Once the data is received, it is deserialised & handled accordingly.
Users connected to the server has access to various commands that offer other functionality than regular messaging.

Further functionality was added through the moderators. Moderators have access to further commands that cannot be used by non-moderator users. The moderator is assigned automatically by the server.

This project was intended to be a culmination of everything that was learnt during the djikstra project.
The project is properly structured with helper classes, doc strings, & comments; & designed to be scalable.
The project features abstraction, multi-threading, regular expressions, python sockets, serialisation, inheritance, pattern matching with enums.

Further improvements could be quite exciting, there is a lot of possibilities with python sockets from bluetooth connectivity to image data transmission. Further commands could always be added.
