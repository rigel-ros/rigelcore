from rigelcore.clients import ROSBridgeClient
from rigelcore.simulations import Command, CommandBuilder, CommandType
from typing import Any, Callable, Dict
from .node import SimulationRequirementNode

ROS_MESSAGE_TYPE = Dict[str, Any]


class SimpleSimulationRequirementNode(SimulationRequirementNode):
    """
    A simple simulation requirement node consists of a node without children.
    Simple simulation requirements interface with ROS bridge clients and hande incoming ROS messages.
    """

    def __init__(
            self,
            ros_topic: str,
            ros_message_type: str,
            ros_message_callback: Callable
            ) -> None:
        """
        Class constructor.
        Selects simulation assessment strategy.

        :param ros_topic: The ROS topic to subscribe.
        :type ros_topic: str
        :param ros_message_type: The type of expected ROS message.
        :type ros_message_type: str
        """
        self.children = []
        self.father = None

        self.ros_topic = ros_topic
        self.ros_message_type = ros_message_type
        self.ros_message_callback = ros_message_callback

    def handle_upstream_command(self, command: Command) -> None:
        pass  # TODO: implement later

    def handle_downstream_command(self, command: Command) -> None:
        """
        Generic command handler.
        Forwards incoming downstream commands to their proper handler.

        :param command: Received downstream command.
        :type command: Command
        """
        if command.type == CommandType.ROSBRIDGE_CONNECT:
            self.connect_to_rosbridge(command.data['client'])
        elif command.type == CommandType.ROSBRIDGE_DISCONNECT:
            self.disconnect_from_rosbridge()

    def connect_to_rosbridge(self, rosbridge_client: ROSBridgeClient) -> None:
        """
        Register ROS message handler and start listening for incoming ROS messages.

        :param rosbridge_client: The ROS bridge client.
        :type rosbridge_client: ROSBridgeClient
        """
        self.__rosbridge_client = rosbridge_client
        self.__rosbridge_client.register_message_handler(
            self.ros_topic,
            self.ros_message_type,
            self.message_handler
        )

    def disconnect_from_rosbridge(self) -> None:
        """
        Unregister ROS message handler and stop listening for incoming ROS messages.
        """
        self.__rosbridge_client.remove_message_handler(
            self.ros_topic,
            self.ros_message_type,
            self.message_handler
        )

    def message_handler(self, message: ROS_MESSAGE_TYPE) -> None:
        """
        ROS message handler.
        Applied predicate condition to all messages in order to assess
        simulation requirement.

        :param message: The received ROS message.
        :type message: ROS_MESSAGE_TYPE
        """
        if self.ros_message_callback(message) != self.satisfied:  # only consider state changes
            self.satisfied = not self.satisfied

            # Inform father node about state change.
            command = CommandBuilder.build_status_change_cmd()
            self.send_upstream_cmd(command)
