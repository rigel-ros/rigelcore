from __future__ import annotations
from rigelcore.clients import ROSBridgeClient
from rigelcore.simulations import Command, CommandBuilder, CommandType
from typing import Any, Callable, Dict, List, Tuple


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

    # All simulation requirements nodes have implement a mechanism
    # that indicates whether or not that requirement was satisfied or not.
    @property
    def satisfied(self) -> bool:
        raise NotImplementedError("Please implement this method")

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


class ExistenceSimulationRequirementNode(SimulationRequirementNode):
    """
    An existence simulation requirement node ensures
    that at least a ROS message was received that satisfies a given condition.
    """

    def __init__(self) -> None:
        self.children = []
        self.father = None

    @property
    def satisfied(self) -> bool:
        """
        Tell whether or not this simulation requirement is satisfied.
        An existence simulation requirement is considered satisfied
        only if all children simulation requirements are also satisfied.
        """
        for child in self.children:
            if not child.satisfied:
                return False
        return True

    def handle_upstream_command(self, command: Command) -> None:
        pass  # TODO: implement later

    def handle_downstream_command(self, command: Command) -> None:
        pass  # TODO: implement later


class AbsenceSimulationRequirementNode(SimulationRequirementNode):
    """
    An absence simulation requirement node ensures
    that no ROS message was received that satisfies a given condition.
    """

    def __init__(self) -> None:
        self.children = []
        self.father = None

    @property
    def satisfied(self) -> bool:
        """
        Tell whether or not this simulation requirement is satisfied.
        An absence simulation requirement is considered satisfied
        only if no children simulation requirements is satisfied.
        """
        for child in self.children:
            if child.satisfied:
                return False
        return True

    def handle_upstream_command(self, command: Command) -> None:
        pass  # TODO: implement later

    def handle_downstream_command(self, command: Command) -> None:
        pass  # TODO: implement later


class ResponseSimulationRequirementNode(SimulationRequirementNode):
    """
    A response simulation requirement node ensures
    that no ROS message is received that satisfies posterior requirements
    before anterior requirements were previously satisfied.
    """

    def __init__(self) -> None:
        self.children = []
        self.father = None

    @property
    def satisfied(self) -> bool:
        """
        Tell whether or not this simulation requirement is satisfied.
        A response simulation requirement consists is considered satisfied
        in any of the following situations:
        - both anterior and posterior requirements are unsatisfied
        - anterior requirements are satisfied and posterior requirements are unsatisfied
        - both anterior and posterior requirements are satisfied
        """
        n_children = len(self.children)
        assert n_children == 2, f'RESPONSE pattern with unexpected number of children {n_children}'

        anterior = self.children[0]
        posterior = self.children[1]
        if not anterior.satisfied:
            if posterior.satisfied:
                return False
        return True

    def handle_upstream_command(self, command: Command) -> None:
        pass  # TODO: implement later

    def handle_downstream_command(self, command: Command) -> None:
        pass  # TODO: implement later


class RequirementSimulationRequirementNode(SimulationRequirementNode):
    """
    A response simulation requirement node ensures
    that if a ROS message is received that satisfies anterior requirements
    then all posterior requirements were already previously satisfied.
    """

    def __init__(self) -> None:
        self.children = []
        self.father = None

    @property
    def satisfied(self) -> bool:
        """
        Tell whether or not this simulation requirement is satisfied.
        A response simulation requirement consists is considered satisfied
        in any of the following situations:
        - both anterior and posterior requirements are unsatisfied
        - posterior requirements are satisfied and anterior requirements are unsatisfied
        - both anterior and posterior requirements are satisfied
        """
        n_children = len(self.children)
        assert n_children == 2, f'REQUIREMENT pattern with unexpected number of children {n_children}'

        posterior = self.children[0]
        anterior = self.children[1]
        if anterior.satisfied:
            if not posterior.satisfied:
                return False
        return True

    def handle_upstream_command(self, command: Command) -> None:
        pass  # TODO: implement later

    def handle_downstream_command(self, command: Command) -> None:
        pass  # TODO: implement later


class PreventionSimulationRequirementNode(SimulationRequirementNode):
    """
    A response simulation requirement node ensures
    that if a ROS message is received that satisfies anterior requirements
    then no other message ROS message is received that satisfies posterior requirements.
    """

    def __init__(self) -> None:
        self.children = []
        self.father = None
        self.__satisfied = False

    @property
    def satisfied(self) -> bool:
        """
        Tell whether or not this simulation requirement is satisfied.
        A prevention simulation requirement consists is considered satisfied
        in any of the following situations:
        - both anterior and posterior requirements are unsatisfied
        - posterior requirements are satisfied and anterior requirements are unsatisfied
        """
        n_children = len(self.children)
        assert n_children == 2, f'REQUIREMENT pattern with unexpected number of children {n_children}'

        anterior = self.children[0]
        posterior = self.children[1]
        if anterior.satisfied:
            if posterior.satisfied:
                return False
        return True

    def handle_upstream_command(self, command: Command) -> None:
        pass  # TODO: implement later - requires state machine

    def handle_downstream_command(self, command: Command) -> None:
        pass  # TODO: implement later - requires state machine


class DisjointSimulationRequirementNode(SimulationRequirementNode):
    """
    A disjoint simulation requirement node consists of a node with at least one child.
    """

    def __init__(self) -> None:
        self.children = []
        self.father = None
        self.__satisfied = False

    @property
    def satisfied(self) -> bool:
        """
        Tell whether or not this simulation requirement is satisfied.

        :rtype: bool
        :return: True if this simulation requirement is satisfied. False otherwise.
        """
        return self.__satisfied

    def assess_children_nodes(self) -> bool:
        """
        A disjoint simulation requirement is considered satisfied
        only when at least one of its children simulation requirements is also satisfied.

        :rtype: bool
        :return: True if this simulation requirement is satisfied. False otherwise.
        """
        for child in self.children:
            if child.satisfied:
                return True
        return False

    def handle_children_status_change(self) -> None:
        result = self.assess_children_nodes()
        if result != self.__satisfied:  # only consider state changes
            self.__satisfied = result

            # Inform father node about state change.
            command = CommandBuilder.build_status_change_cmd()
            self.send_upstream_cmd(command)

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
            self.send_downstream_cmd(command)


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

        self.__satisfied = False

    @property
    def satisfied(self) -> bool:
        return self.__satisfied

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
        # TODO: start counting time

    def disconnect_from_rosbridge(self) -> None:
        """
        Unregister ROS message handler and stop listening for incoming ROS messages.
        """
        self.__rosbridge_client.remove_message_handler(
            self.ros_topic,
            self.ros_message_type,
            self.message_handler
        )
        # TODO: stop counting time

    def message_handler(self, message: ROS_MESSAGE_TYPE) -> None:
        """
        ROS message handler.
        Applied predicate condition to all messages in order to assess
        simulation requirement.

        :param message: The received ROS message.
        :type message: ROS_MESSAGE_TYPE
        """
        if self.ros_message_callback(message):  # only consider state changes
            self.__satisfied = True

            # Disconnect from ROS bridge.
            self.disconnect_from_rosbridge()

            # Inform father node about state change.
            command = CommandBuilder.build_status_change_cmd()
            self.send_upstream_cmd(command)
