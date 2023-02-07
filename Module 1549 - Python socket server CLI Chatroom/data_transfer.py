import pickle
import sys
import time
import socket
import typing

import data_types

# Delay between data in message header packets.
# If the delay is too low, then recieve() will miss some incoming packets.
MESSAGE_PACKET_DELAY = 0.1

class DataTransfer:
    """
    Package data for serialisation/ deserialisation & send/ receive that data to/ from sockets

    Utility class for sending & receiving data over python sockets.
    The class does not needs to be instantiated.
    The class handles the receive size, packaging & unpackaging the data, & returns a dictionary of all the data.
    """
    @staticmethod
    def transmit(data, recipient_socket: socket.socket, data_type: data_types.TransmissionDataType):
        """
        Send the data to the socket.
        
        transmit() will package the data to be sent, add the header buffer, & predefined fixed header size.
        Data is sent as serialised objects, by the pickle module, & deserialised by the pickle module again once received by the socket.
        """
        try:
            # Header with data size, recipient, & data type.
            recipient_socket.send(pickle.dumps(dict(data_byte_size = sys.getsizeof(data), data_type = data_type)))
            time.sleep(MESSAGE_PACKET_DELAY)
            # Actual data to be acted upon by the recipient socket.
            recipient_socket.send(pickle.dumps(dict(data = data)))
            time.sleep(MESSAGE_PACKET_DELAY)
        except OSError:
            return

    @staticmethod
    def receive(receiving_socket: socket.socket) -> typing.Union[dict, None]:
        """
        Receive the data from the socket
        
        recv() will unpackage the data received.
        The data arrives as serialised objects, by the pickle module, & deserialised by the pickle module again.
        The deserialised objects are dictionary's with all the data that was trasmitted.
        """
        try:
            # # Receive detailing the actual data to arrive.
            data = pickle.loads(receiving_socket.recv(252))
            time.sleep(MESSAGE_PACKET_DELAY)
            # Variable-byte-size receive to receive the data to be acted upon by the recipient.
            data.update(pickle.loads(receiving_socket.recv(data['data_byte_size'])))
            time.sleep(MESSAGE_PACKET_DELAY)

            return data
        # client disconnects from server
        except ConnectionAbortedError:
            return
        # client disconnects from server (above), raises OSError next
        except OSError:
            return