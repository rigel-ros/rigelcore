from rigelcore.simulations import Command, CommandBuilder, CommandType
from .node import SimulationRequirementNode


class ResponseSimulationRequirementNode(SimulationRequirementNode):
    """
    A response simulation requirement node ensures
    that no ROS message is received that satisfies posterior requirements
    before anterior requirements were previously satisfied.
    """

    def __init__(self) -> None:
        self.children = []
        self.father = None

        # By default a response simulation requirement is considered satisfied.
        # due to he existence of both an unsatisfied anterior and an unsatisfied posterior reqirements.
        self.satisfied = True

    def assess_children_nodes(self) -> bool:
        """
        A response simulation requirement consists is considered satisfied
        in any of the following situations:
        - both anterior and posterior requirements are satisfied
        """
        n_children = len(self.children)
        assert n_children == 2, f'RESPONSE pattern with unexpected number of children {n_children}'

        anterior = self.children[0]
        posterior = self.children[1]
        return anterior.satisfied and posterior.satisfied

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
