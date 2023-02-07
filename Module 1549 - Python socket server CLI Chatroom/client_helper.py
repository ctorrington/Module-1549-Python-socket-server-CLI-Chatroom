import socket
import re

import data_transfer
import data_types
import client

class ClientHelper:
    def handle_send_message(self, client_instance: client.Client, message) -> None:
            # Command input.
            if re.search('^\\\\', message):
                # Determine which command is being input.
                if re.search('^\\\\members', message):
                    data_transfer.DataTransfer.transmit("members request", client_instance.client_socket, data_types.TransmissionDataType.REQUEST_MEMBER_LIST)

                if re.search('^\\\\leave', message):
                    print("Are you sure you would like to leave? Y/n")
                    if input() in ["", "Yes", "yes", "Y", "y"]:
                        data_transfer.DataTransfer.transmit("client disconnected", client_instance.client_socket, data_types.TransmissionDataType.CLIENT_DISCONNECTED)
                        client_instance.client_socket.close()
                        client_instance.client_status_flag[0] = False

                if re.search('^\\\\help', message):
                    data_transfer.DataTransfer.transmit("help", client_instance.client_socket, data_types.TransmissionDataType.HELP)

                if re.search('^\\\\w', message) or re.search('^\\\\whisper', message):
                    data_transfer.DataTransfer.transmit(message, client_instance.client_socket, data_types.TransmissionDataType.WHISPER)

                if re.search('^\\\\kick', message):
                    kick_member = message[message.find(" ") + 1::]
                    print(f"Are you sure you would like to kick {kick_member}? Y/n")
                    print("This feature is coming soon (:")
                    # if input() in ["", "Yes", "yes", "Y", "y"]:
                    #     data_transfer.DataTransfer.transmit(message, client_instance.client_socket, data_types.TransmissionDataType.KICK_MEMBER)

            # Regular message input.
            else:
                if client_instance.username_flag[0]:
                    data_transfer.DataTransfer.transmit(message, client_instance.client_socket, data_types.TransmissionDataType.USERNAME_SETUP)
                    client_instance.username_flag = [False]
                else:
                    data_transfer.DataTransfer.transmit(message, client_instance.client_socket, data_types.TransmissionDataType.BROADCAST)