import threading
from math import inf
from rigelcore.simulations import Command, CommandBuilder, CommandType
from .node import SimulationRequirementNode


class RequirementSimulationRequirementNode(SimulationRequirementNode):
    """
    A response simulation requirement node ensures
    that if a ROS message is received that satisfies anterior requirements
    then all posterior requirements were already previously satisfied.
    """

    def __init__(self, timeout: float = inf) -> None:
        self.children = []
        self.father = None
        self.__timeout = timeout

    def assess_children_nodes(self) -> bool:
        """
        A response simulation requirement consists is considered satisfied
        in any of the following situations:
        - both anterior and posterior requirements are satisfied
        """
        n_children = len(self.children)
        assert n_children == 2, f'REQUIREMENT pattern with unexpected number of children {n_children}'

        posterior = self.children[0]
        anterior = self.children[1]
        return posterior.satisfied and anterior.satisfied

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
