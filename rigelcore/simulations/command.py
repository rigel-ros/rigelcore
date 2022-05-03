from enum import Enum
from rigelcore.clients import ROSBridgeClient
from typing import Any, Dict


class CommandType(Enum):
    ROSBRIDGE_CONNECT: int = 1
    ROSBRIDGE_DISCONNECT: int = 2
    STATUS_CHANGE: int = 3


class Command:
    """
    A command to be exchanged between simulation requirement nodes.
    """
    def __init__(self, type: CommandType, data: Dict[str, Any]) -> None:
        self.type = type
        self.data = data


class CommandBuilder:
    """
    A class to uniformize the creation of Command instances.
    """

    @staticmethod
    def build_rosbridge_connect_cmd(rosbridge_client: ROSBridgeClient) -> Command:
        """
        Build a command that instructs requirement nodes to connect to a ROS bridge client.

        :param rosbridge_client: The ROS bridge client instance.
        :type rosbridge_client: ROSBridgeClient
        :return: A command holding necessary information.
        :rtype: Command
        """
        return Command(
            CommandType.ROSBRIDGE_CONNECT,
            {'client': rosbridge_client}
        )

    @staticmethod
    def build_rosbridge_disconnect_cmd() -> Command:
        """
        Build a command that instructs requirement nodes to disconnect from a ROS bridge client.

        :return: A command holding necessary information.
        :rtype: Command
        """
        return Command(
            CommandType.ROSBRIDGE_DISCONNECT,
            {}
        )

    @staticmethod
    def build_status_change_cmd() -> Command:
        """
        Build a command that informs requirement nodes that a children node's state has changed.

        :return: A command holding necessary information.
        :rtype: Command
        """
        return Command(
            CommandType.STATUS_CHANGE,
            {}
        )
