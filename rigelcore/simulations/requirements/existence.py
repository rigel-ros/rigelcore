from rigelcore.simulations import Command, CommandBuilder, CommandType
from .node import SimulationRequirementNode


class ExistenceSimulationRequirementNode(SimulationRequirementNode):
    """
    An existence simulation requirement node ensures
    that at least a ROS message was received that satisfies a given condition.
    """

    def __init__(self) -> None:
        self.children = []
        self.father = None

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

    def handle_upstream_command(self, command: Command) -> None:
        if command.type == CommandType.STATUS_CHANGE:
            self.handle_children_status_change()

    def handle_downstream_command(self, command: Command) -> None:
        pass  # TODO: implement later
