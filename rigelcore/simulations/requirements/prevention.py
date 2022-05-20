import threading
from math import inf
from rigelcore.simulations.command import Command, CommandBuilder, CommandType
from .node import SimulationRequirementNode


class PreventionSimulationRequirementNode(SimulationRequirementNode):
    """
    A response simulation requirement node ensures
    that if a ROS message is received that satisfies anterior requirements
    then no other message ROS message is received that satisfies posterior requirements.
    """

    def __init__(self, timeout: float = inf) -> None:
        self.children = []
        self.father = None
        self.timeout = timeout
        self.__timer = threading.Timer(timeout, self.handle_timeout)

    def assess_children_nodes(self) -> bool:
        """
        A prevention simulation requirement consists is considered satisfied
        in any of the following situations:
        - posterior requirements are satisfied and anterior requirements are unsatisfied
        """
        n_children = len(self.children)
        assert n_children == 2, f'REQUIREMENT pattern with unexpected number of children {n_children}'

        anterior = self.children[0]
        posterior = self.children[1]

        # If the posterior requirement is satisfied after the anterior requirement
        # then a point of no return if reached and the assessment can be stopped.
        if anterior.satisfied and posterior.satisfied:
            command = CommandBuilder.build_stop_simulation_cmd()
            self.send_upstream_cmd(command)

        return False

    def handle_children_status_change(self) -> None:
        """
        Handle STATUS_CHANGE commands sent by children nodes.
        Whenever a child changes state a disjoint requirement node must check its satisfability.
        """
        if self.assess_children_nodes() != self.satisfied:  # only consider state changes
            self.satisfied = not self.satisfied

            self.__timer.cancel()

            # Issue children to stop receiving incoming ROS messages.
            command = CommandBuilder.build_rosbridge_disconnect_cmd()
            self.send_downstream_cmd(command)

            # Inform father node about state change.
            command = CommandBuilder.build_status_change_cmd()
            self.send_upstream_cmd(command)

    def handle_timeout(self) -> None:
        """
        Handle timeout events.
        Issue children nodes to stop listening for ROS messages.
        """
        anterior = self.children[0]
        posterior = self.children[1]
        self.satisfied = anterior.satisfied and not posterior.satisfied

        if not self.satisfied:
            command = CommandBuilder.build_stop_simulation_cmd()
            self.send_upstream_cmd(command)

    def handle_rosbridge_connection_commands(self, command: Command) -> None:
        """
        Handle commands of type ROSBRIDGE_CONNECT.
        Forward command to all children nodes and initialize timer thread.

        :param command: Received command.
        :type command: Command
        """
        self.send_downstream_cmd(command)

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
        anterior = self.children[0]
        posterior = self.children[1]
        self.satisfied = anterior.satisfied and not posterior.satisfied

        self.__timer.cancel()  # NOTE: this method does not require previous call to 'start()'
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
