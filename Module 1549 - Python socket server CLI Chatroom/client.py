import socket
import threading
import client_helper

import data_transfer
import data_types

class Client:
    """Connect to python socket server to send & receive data from other connected clients"""
    
    def __init__(self) -> None:
        self.client_address = None
        self.client_port = None
        self.client_ID = None
        self.username_flag = [False]
        self.client_status_flag = [True]
        self.client_helper_object = client_helper.ClientHelper()

    def setup(self) -> None:
        """Create & connect the client's socket to the server & set their username"""

        # self.client_address = input("enter server address: ")
        # self.client_port = int(input(f"enter {self.client_address} server port: "))
        self.client_address = "127.0.0.1" # tmp
        self.client_port = 65000 # tmp
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.client_address, self.client_port))
        if self.client_socket is not None:

            self.client_ID = input("enter your name:")
            data_transfer.DataTransfer.transmit(self.client_ID, self.client_socket, data_types.TransmissionDataType.USERNAME_SETUP)

            # Start a new thread for sending text entered by the client to the server.
            # The main thread continues through receive()
            self.receive_from_server_thread = threading.Thread(target = self.send)
            self.receive_from_server_thread.start()

            self.receive()

    def receive(self) -> None:
        """Handle receiving data sent from the connected server socket"""
        
        while self.client_status_flag[0]:
            try:
                data = data_transfer.DataTransfer.receive(self.client_socket)
                if data:
                    match data["data_type"]:
                        # Client handle cases.
                        case data_types.TransmissionDataType.BROADCAST:
                            print(data["data"])

                        case data_types.TransmissionDataType.WHISPER:
                            print(data["data"])

                        case data_types.TransmissionDataType.SERVER_MESSAGE:
                            print(data["data"])

                        case data_types.TransmissionDataType.USERNAME_SETUP:
                            print(data["data"])
                            self.username_flag = [True]

                        case data_types.TransmissionDataType.REQUEST_MEMBER_LIST:
                            for i in data["data"]:
                                print(i)
                            
                        case data_types.TransmissionDataType.HELP:
                            for i in data["data"]:
                                print(i)

                        case data_types.TransmissionDataType.KICK_MEMBER:
                            self.client_socket.close()

                        case other:
                            print("other data type found")

            except ValueError:
                print("You have been removed for inactivity.")
                self.client_status_flag = [False]
                self.client_socket.close()
                return


    def send(self) -> None:
        """Send text entered by the client to the server."""

        while self.client_status_flag[0]:
            message = input()

            self.client_helper_object.handle_send_message(self, message)

def main() -> None:
    client_object = Client()
    client_object.setup()

if (__name__ == "__main__"):
    main()
