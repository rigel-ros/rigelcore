from rigelcore.simulations import Command, CommandBuilder, CommandType
from .node import SimulationRequirementNode


class PreventionSimulationRequirementNode(SimulationRequirementNode):
    """
    A response simulation requirement node ensures
    that if a ROS message is received that satisfies anterior requirements
    then no other message ROS message is received that satisfies posterior requirements.
    """

    def __init__(self) -> None:
        self.children = []
        self.father = None

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
        return anterior.satisfied and not posterior.satisfied

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
        pass  # TODO: implement later - requires state machine
