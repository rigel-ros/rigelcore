import threading
from math import inf
from rigelcore.simulations.command import Command, CommandBuilder, CommandType
from .node import SimulationRequirementNode


class ResponseSimulationRequirementNode(SimulationRequirementNode):
    """
    A response simulation requirement node ensures
    that no ROS message is received that satisfies posterior requirements
    before anterior requirements were previously satisfied.
    """

    def __init__(self, timeout: float = inf) -> None:
        self.children = []
        self.father = None
        self.timeout = timeout
        self.__timer = threading.Timer(timeout, self.handle_timeout)

    def assess_children_nodes(self) -> bool:
        """
        A response simulation requirement is considered satisfied
        only if the posterior requirement is satisfied after the anterior requirement.

        :rtype: bool
        :return: True is requirement is satisfied. False otherwise.
        """
        anterior = self.children[0]
        posterior = self.children[1]
        return anterior.satisfied and posterior.satisfied

    def handle_timeout(self) -> None:
        """
        Handle timeout events.
        Issue children nodes to stop listening for ROS messages.
        """
        self.satisfied = self.assess_children_nodes()
        if self.satisfied:
            self.send_upstream_cmd(CommandBuilder.build_status_change_cmd())
            self.send_downstream_cmd(CommandBuilder.build_rosbridge_disconnect_cmd())
        else:
            # If the posterior requirement is satisfied before the anterior one
            # then a point of no return if reached and the assessment can be stopped.
            self.send_upstream_cmd(CommandBuilder.build_stop_simulation_cmd())

    def handle_children_status_change(self) -> None:
        """
        Handle STATUS_CHANGE commands sent by children nodes.
        Whenever a child changes state a disjoint requirement node must check its satisfability.
        """
        posterior = self.children[1]
        if not posterior.listening:  # true right after anterior requirement was satisfied
            self.send_child_downstream_cmd(posterior, self.__connect_command)

        else:
            self.satisfied = self.assess_children_nodes()
            if self.satisfied:
                self.__timer.cancel()
                self.send_downstream_cmd(CommandBuilder.build_rosbridge_disconnect_cmd())
                self.send_upstream_cmd(CommandBuilder.build_status_change_cmd())

    def handle_rosbridge_connection_commands(self, command: Command) -> None:
        """
        Handle commands of type ROSBRIDGE_CONNECT.
        Forward command to all children nodes and initialize timer thread.

        :param command: Received command.
        :type command: Command
        """
        self.__connect_command = command  # save command to be sent later to posterior

        # Notify only the anterior requirement node.
        # Posterior node must only start listening for ROS messages after it being satisfied.
        anterior = self.children[0]
        self.send_child_downstream_cmd(anterior, command)

        # NOTE: code below will only execute after all ROS message handler were registered.
        if self.timeout != inf:  # start timer in case a time limit was specified
            self.__timer.start()

    def handle_rosbridge_disconnection_commands(self, command: Command) -> None:
        """
        Handle commands of type ROSBRIDGE_DISCONNECT.
        Forwars command to all children nodes and stop timer threads.

        :param command: Received command.
        :type command: Command
        """
        self.__timer.cancel()  # NOTE: this method does not require previous call to 'start()'

        self.satisfied = self.assess_children_nodes()
        if self.satisfied:
            self.send_upstream_cmd(CommandBuilder.build_status_change_cmd())

        self.send_downstream_cmd(command)

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
        if command.type == CommandType.ROSBRIDGE_DISCONNECT:
            self.handle_rosbridge_disconnection_commands(command)
