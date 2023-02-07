from enum import Enum

class TransmissionDataType(Enum):
    """"
    Distinguish between data types.
    
    Helper class for server & client modules.
    """
    BROADCAST = 1
    WHISPER = 2
    SERVER_MESSAGE = 3
    LEAVE = 4
    KICK_MEMBER = 5
    REQUEST_MEMBER_LIST = 6
    USERNAME_SETUP = 7
    CLIENT_DISCONNECTED = 8
    HELP = 9