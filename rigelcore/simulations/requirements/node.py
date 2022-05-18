from __future__ import annotations
from rigelcore.simulations import Command
from typing import Any, Dict, List, Tuple


ROS_MESSAGE_TYPE = Dict[str, Any]
PREDICATE_TYPE = Tuple[str, str, str]


class SimulationRequirementNode:
    """
    Simulation requirements are hierarchical.
    This class serves as a base class for all simulation requirenents tree node
    and declares the interface that they must comply with.
    """

    # Simulation requirements nodes form a hierarchical tree.
    # For commands to be exchanged between tree layers
    # each node must have a local notion of the tree structure.
    father: SimulationRequirementNode
    children: List[SimulationRequirementNode]

    # All simulation requirements nodes have a flag
    # that indicates whether or not that requirement was satisfied.
    satisfied: bool = False

    # All simulations requirements node must implement a mechanism
    # to handle upstream commands sent by their resprective children nodes.
    def handle_upstream_command(self, command: Command) -> None:
        raise NotImplementedError("Please implement this method")

    # All simulations requirements node must implement a mechanism
    # to handle downstream commands sent by their resprective father node.
    def handle_downstream_command(self, command: Command) -> None:
        raise NotImplementedError("Please implement this method")

    # All simulation requirements nodes may send upstream commands
    # to their respective father nodes.
    def send_upstream_cmd(self, command: Command) -> None:
        """
        Send a upstream command to the father node.

        :type command: Command
        :param command: The upstream command to send to the father node.
        """
        if self.father:
            self.father.handle_upstream_command(command)

    # All simulation requirements nodes may send downstream commands
    # to their respective children nodes.
    def send_downstream_cmd(self, command: Command) -> None:
        """
        Send a downstream command to all children nodes.

        :type command: Command
        :param command: The downstream command to send to all children nodes.
        """
        for child in self.children:
            child.handle_downstream_command(command)
