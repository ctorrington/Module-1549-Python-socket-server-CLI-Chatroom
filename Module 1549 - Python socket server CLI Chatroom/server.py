import socket
import threading

import data_transfer
import data_types
import server_helper

class Server():
    """
    Passive server functionality for client communication.

    Open a python socket to handle connections & relay transferred data between connected sockets.
    """
    def __init__(self, server_address: str, server_port: int) -> None: 
        """Setup class variables & server socket type"""

        self.server_address = server_address
        self.server_port = int(server_port)
        self.members = dict()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.moderator = list()
        self.timeout_delay = 600
        self.client_commands = ["members", "leave", "whisper (w)"]
        self.moderator_commands = ["kick"]
        self.server_helper_object = server_helper.ServerHelper()

    def start_server(self) -> None:
        """Bind server socket to server address, enable server to accept connections & beging accepting connections"""

        print("serving server at ", self.server_address, " on port ", self.server_port)
        self.server_socket.bind((self.server_address, self.server_port))
        self.server_socket.listen()
        self.accept_connections()

    def accept_connections(self) -> None:
        """Accept connections to server, start new threads for connecting clients"""

        while True:
            print("Waiting for connections.")
            client_socket, client_address = self.server_socket.accept()
            client_socket.settimeout(self.timeout_delay)
            print(f"Connection from: {str(client_address)}")

            # Start new thread for every connected client.  Client sockets will have dedicated threads to handle their receive methods.
            receive_from_client_thread = threading.Thread(target = self.receive, name = client_address, args = (client_socket, client_address, [True]))
            receive_from_client_thread.start()

    def receive(self, client_socket: socket.socket, client_address, client_connected_flag: list) -> None:
        """Handle receving data from the connected client socket"""

        while client_connected_flag[0]:
            # receive() is blocking. Wait for data tp be received.
            data = data_transfer.DataTransfer.receive(client_socket)

            if data:      
                # Match the received data type to handle cases.
                match data["data_type"]:
                    # Server handle cases
                    case data_types.TransmissionDataType.BROADCAST:
                        # self.handle_receive_broadcast(data, client_socket)
                        self.server_helper_object.handle_receive_broadcast(self, data, client_socket)

                    case data_types.TransmissionDataType.WHISPER:
                        # self.handle_receive_whisper(data, client_socket)
                        self.server_helper_object.handle_receive_whisper(self, data, client_socket)

                    # Server helper handle cases
                    case data_types.TransmissionDataType.USERNAME_SETUP:
                        # self.handle_receive_username_setup(data, client_socket, client_address)
                        self.server_helper_object.handle_receive_username_setup(self, data, client_socket, client_address)

                    case data_types.TransmissionDataType.REQUEST_MEMBER_LIST:
                        # self.handle_receive_request_member_list(client_socket)
                        self.server_helper_object.handle_receive_request_member_list(self, client_socket)

                    case data_types.TransmissionDataType.CLIENT_DISCONNECTED:
                        client_connected_flag[0] = self.client_disconnected(client_socket)
                        # self.server_helper_object.handle_

                    case data_types.TransmissionDataType.HELP:
                        # self.handle_receive_help(client_socket)
                        self.server_helper_object.handle_receive_help(self, client_socket)

                    case data_types.TransmissionDataType.KICK_MEMBER:
                        # self.handle_receive_kick_member(client_socket)
                        self.server_helper_object.handle_receive_kick_member(self, client_socket, data)

                    case other:
                        # This should never be reached.
                        print("Server data_type other case called.")

            else:
                client_connected_flag[0] = self.client_disconnected(client_socket)

    def client_disconnected(self, client_socket: socket.socket) -> bool:
        """Handle client disconnecting from the server"""

        # Check whether the client had been added to the members list.
        if client_socket in self.members:

            # Remove the socket from the members dictionary
            data = dict()
            print(f"{self.members[client_socket][1]} disconnected.")
            data["data"] = self.members[client_socket][1] + " has disconnected from the server."
            self.broadcast_message(data, data_types.TransmissionDataType.SERVER_MESSAGE)
            del self.members[client_socket]
            self.server_helper_object.remove_moderator(self, client_socket)

        # Close the client socket & stop the client's receive() loop.
        client_socket.close()
        return False

    # broadcast a message to all members
    def broadcast_message(self, data, data_type: data_types.TransmissionDataType) -> None:
        """Send data to every client connected to the server"""

        match data_type:
            case data_types.TransmissionDataType.BROADCAST:
                data["data"] = data['sender'] + ": " + data['data']

            case data_types.TransmissionDataType.WHISPER:
                pass

            case data_types.TransmissionDataType.SERVER_MESSAGE:
                pass

            case other:
                print("Server.broadcast_message() other case called")


        for client_socket in self.members:
            self.direct_message(data["data"], client_socket, data_type)

    # send message to only one client
    def direct_message(self, data, recipient_socket, data_type) -> None:
        """Send data to the recipient socket (client)"""

        print(f"tranmitting: {data}")
        data_transfer.DataTransfer.transmit(data, recipient_socket, data_type)

def main() -> None:
    """Initialises the Server object"""

    # server_address = input("enter server address: ")
    # server_port = input(f"enter server port: ")
    server_address = "127.0.0.1"  #  temp
    server_port = 65000  #  temp
    server_object = Server(server_address, server_port)
    server_object.start_server()

if __name__ == "__main__":
    main()