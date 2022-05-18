import threading
from math import inf
from rigelcore.simulations import Command, CommandBuilder, CommandType
from .node import SimulationRequirementNode


class ExistenceSimulationRequirementNode(SimulationRequirementNode):
    """
    An existence simulation requirement node ensures
    that at least a ROS message was received that satisfies a given condition.
    """

    def __init__(self, timeout: float = inf) -> None:
        self.children = []
        self.father = None
        self.__timeout = timeout

    def assess_children_nodes(self) -> bool:
        """
        An existence simulation requirement is considered satisfied
        only if all children simulation requirements are also satisfied.

        :rtype: bool
        :return: True if all children simulation requirements are satisfied. False otherwise.
        """
        for child in self.children:
            if not child.satisfied:
                return False
        return True

    def handle_children_status_change(self) -> None:
        """
        Handle STATUS_CHANGE commands sent by chilren nodes.
        Whenever a child changes state a disjoint requirement node must check its satisfability.
        """
        if self.assess_children_nodes() != self.satisfied:  # only consider state changes
            self.satisfied = not self.satisfied

            # Inform father node about state change.
            command = CommandBuilder.build_status_change_cmd()
            self.send_upstream_cmd(command)

    def handler_timeout(self) -> None:
        """
        Handle timeout events.
        Issue children nodes to stop listening for ROS messages.
        """
        command = CommandBuilder.build_rosbridge_disconnect_cmd()
        self.send_downstream_cmd(command)

        if not self.satisfied:
            # TODO: find mechanism to stop simulation!!!
            pass

    def handle_rosbridge_connection_commands(self, command: Command) -> None:
        """
        Handle commands of type STATUS_CHANGE.
        Forward command to all children nodes and initialize timer thread.

        :param command: Received command.
        :type command: Command
        """
        self.send_downstream_cmd(command)

        # NOTE: code below will only execute after all ROS message handler were registered.
        if self.__timeout != inf:  # start timer in case a time limit was specified
            timer = threading.Timer(self.__timeout, self.handle_timeout)
            timer.start()

    def handle_upstream_command(self, command: Command) -> None:
        """
        Generic command handler.
        Forwards incoming upstream commands to their proper handler.

        :param command: Received upstream command.
        :type command: Command
        """
        if command.type == CommandType.STATUS_CHANGE:
            self.handle_children_status_change()

    def handle_downstream_command(self, command: Command) -> None:
        """
        Generic command handler.
        Forwards incoming downstream commands to their proper handler.

        :param command: Received dowstream command.
        :type command: Command
        """
        if command.type == CommandType.ROSBRIDGE_CONNECT:
            self.handle_rosbridge_connection_commands(command)
