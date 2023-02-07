import socket

import data_transfer
import data_types
import server

class ServerHelper:
    """Handle data received by the server, & server moderation"""
    
    def handle_receive_broadcast(self, server_instance: server.Server, data, client_socket: socket.socket):
            """Hanlde data when data type is BROADCAST"""

            print(f"BROADCAST from {server_instance.members[client_socket][1]}: {data['data']}")
            data.update({"sender": server_instance.members[client_socket][1]})
            server_instance.broadcast_message(data, data_types.TransmissionDataType.BROADCAST)

    def handle_receive_whisper(self, server_instance: server.Server, data, client_socket: socket.socket):
        """Handle data when data type is WHISPER"""

        print(f"WHISPER from {server_instance.members[client_socket][1]}: {data['data']}")
        data.update({"sender": server_instance.members[client_socket][1]})

        # Check whether client entered '\w' or '\whisper' command.
        recipient_index = data["data"].find('\\w ')
        if recipient_index == -1:
            recipient_index = len('\\whisper ')
        else:
            recipient_index = len('\\w ')

        # Find the intended whisper recipient.
        recipient = data["data"][recipient_index:data["data"].find(' ', recipient_index)]

        # Remove the command prefix from the whispered message, ie: '\w client_username'.
        data["data"] = data["data"][(recipient_index + len(recipient) + 1)::]

        # Construct the final whispered message syntax to be transmitted.
        data["data"] = data["sender"] + (" (whispers): ") + data["data"]

        # Find the whisper recipient socket & transmit data.
        for socket in server_instance.members:
            if server_instance.members[socket][1] == recipient:
                server_instance.direct_message(data["data"], socket, data_types.TransmissionDataType.WHISPER)
                break

    def handle_receive_username_setup(self, server_instance: server.Server, data, client_socket: socket.socket, client_address):
        """Handle data when data type is USERNAME_SETUP"""

        print(f"USERNAME_SETUP for {client_address}")
        # Check whether username already in use.
        for i in server_instance.members:
            if data["data"] == server_instance.members[i][1]:
                print(f"{data['data']} username already in use.")
                data_transfer.DataTransfer.transmit("That username is already taken. Please enter another on the line below:", client_socket, data_types.TransmissionDataType.USERNAME_SETUP)
                break
        else:
            # Username is unique & accepted.
            server_instance.members[client_socket] = [client_address, data["data"]]
            print(f"Username: {data['data']}, accepted.")
            data["data"] = server_instance.members[client_socket][1] + " has connected to the server."
            server_instance.broadcast_message(data, data_types.TransmissionDataType.SERVER_MESSAGE)
            
            # Check whether client will get moderator role.
            self.moderator_check(server_instance)

    def handle_receive_request_member_list(self, server_instance: server.Server, client_socket: socket.socket):
        """Handle data when data type is REQUEST_MEMBER_LIST"""

        print(f"REQUEST_MEMBER_LIST from {server_instance.members[client_socket][1]}.")
        # Send current list of members to requesting client.
        usernames_list = list()
        for i in server_instance.members:
            usernames_list.append(server_instance.members[i][1])
        server_instance.direct_message(usernames_list, client_socket, data_types.TransmissionDataType.REQUEST_MEMBER_LIST)

    def handle_receive_help(self, server_instance: server.Server, client_socket: socket.socket):
        """Send the commands available to the requesting client"""
        command_list = list()
        command_list.append("Client commands:")            
        for i in server_instance.client_commands:
                command_list.append(i)
        
        if self.is_moderator(server_instance, client_socket):
            command_list.append("\nModerator commands:")
            for i in server_instance.moderator_commands:
                command_list.append(i)

        server_instance.direct_message(command_list, client_socket, data_types.TransmissionDataType.HELP)

    def handle_receive_kick_member(self, server_instance: server.Server, client_socket:socket.socket, data):
        """Check whether a client can kick another client & remove that client if possible"""

        if self.is_moderator(server_instance, client_socket):
            # Find client username to kick.
            kick_client_username = data["data"][data["data"].find(" ") + 1::]

            # Find client socket, by client username, to kick from server.
            for kick_client_socket in server_instance.members:
                if server_instance.members[kick_client_socket][1] == kick_client_username:
                    server_instance.direct_message("kick_member", kick_client_socket, data_types.TransmissionDataType.KICK_MEMBER)
                    data = dict()
                    data["data"] = f"{server_instance.members[kick_client_socket][1]} has been kicked from the server by {server_instance.members[client_socket][1]}."
                    server_instance.broadcast_message(data, data_types.TransmissionDataType.SERVER_MESSAGE)
                    break
            else:
                # Client username was not found.
                server_instance.direct_message(f"Username {kick_client_username} not found.", server_instance.moderator[0], data_types.TransmissionDataType.SERVER_MESSAGE)
        else:
            server_instance.direct_message("You do not have permission to that.", client_socket, data_types.TransmissionDataType.SERVER_MESSAGE)

    def is_moderator(self, server_instance: server.Server, client_socket: socket.socket) -> bool:
        """Return whether the given client is the moderator or not"""

        if server_instance.moderator[0] == client_socket:
            return True
        else:
            return False

    def moderator_check(self, server_instance: server.Server) -> None:
        """Check whether there currently is a moderator"""
        
        if len(server_instance.moderator) == 0:
            self.assign_new_moderator(server_instance)

    def remove_moderator(self, server_instance: server.Server, client_socket: socket.socket) -> None:
        """Check whether the disconnecting client is the moderator, remove if they are, & beging assiging a new moderator"""

        if server_instance.moderator[0] == client_socket:
            del server_instance.moderator[0]
            self.assign_new_moderator(server_instance)


    def assign_new_moderator(self, server_instance: server.Server) -> None:
        """Assign a new client to the moderator role"""

        # Check there are any members connected to the server.
        if len(server_instance.members) > 0:
            # Assign any member as the new moderator.
            server_instance.moderator.append(list(server_instance.members)[0])

            print(f"Assigning {server_instance.members[server_instance.moderator[0]][1]} as the new moderator.")
            server_instance.direct_message("You are the server moderator.", server_instance.moderator[0], data_types.TransmissionDataType.SERVER_MESSAGE)