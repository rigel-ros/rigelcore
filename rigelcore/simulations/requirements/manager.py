import threading
from .node import SimulationRequirementNode
from rigelcore.clients import ROSBridgeClient
from rigelcore.simulations.command import Command, CommandBuilder, CommandType


class SimulationRequirementsManager(SimulationRequirementNode):
    """
    A simulation requirements manager is responsible for
    controling all different node trees associated with a given simulation.
    """

    def __init__(self, max_timeout: float, min_timeout: float = 0.0) -> None:
        self.children = []
        self.father = None
        self.finished = False

        self.__start_timer = threading.Timer(min_timeout, self.handle_start_timeout)
        self.__stop_timer = threading.Timer(max_timeout, self.handle_stop_timeout)

    def connect_to_rosbridge(self, rosbridge_client: ROSBridgeClient):
        """
        Issues children nodes to start listening for incoming ROS messages.

        :param rosbridge_client: The ROS bridge client.
        :type rosbridge_client: ROSBridgeClient
        """
        command = CommandBuilder.build_rosbridge_connect_cmd(rosbridge_client)
        self.send_downstream_cmd(command)

        self.__start_timer.start()
        self.__stop_timer.start()

    def disconnect_from_rosbridge(self):
        """
        Issue children nodes to stop listening for incoming ROS messages.
        """
        command = CommandBuilder.build_rosbridge_disconnect_cmd()
        self.send_downstream_cmd(command)

    def stop_timers(self):
        self.__start_timer.cancel()
        self.__stop_timer.cancel()

    def stop_simulation(self):
        """
        Stop simulation.
        """
        self.disconnect_from_rosbridge()
        self.finished = True

    def handle_start_timeout(self) -> None:
        """
        Allow simulation to be assessed.
        """
        # Ensure that manager detects if all children requirements are
        # already satisfied whenever the simulation starts.
        # For this emulate reception of a STATUS_CHANGE command.
        self.handle_children_status_change()

    def handle_stop_timeout(self) -> None:
        self.stop_simulation()

    def assess_children_nodes(self) -> bool:
        """
        Tell whether or not all simulation requirements were satisfied.

        :return: True if all simulation requirements were satisfied. False otherwise.
        :rtype: bool
        """
        if self.children:
            return False not in [child.satisfied for child in self.children]
        return False  # when no requirements are specified run simulation until timeout is reached.

    def handle_children_status_change(self) -> None:
        """
        Handle STATUS_CHANGE commands sent by children nodes.
        Whenever a child changes state a requirement node must check its satisfability.
        """
        if self.assess_children_nodes() != self.satisfied:  # only consider state changes
            self.satisfied = not self.satisfied
            # Stop simulation once all requirements are .
            if self.satisfied:
                self.stop_timers()
                self.stop_simulation()

    def handle_stop_simulation(self) -> None:
        """
        Handle STOP_SIMULATON commands sent by children nodes.
        Stops simulation and signals its ending.
        """
        self.stop_timers()
        self.stop_simulation()

    def handle_upstream_command(self, command: Command) -> None:
        """
        Generic command handler.
        Forwards incoming upstream commands to their proper handler.

        :param command: Received upstream command.
        :type command: Command
        """
        if command.type == CommandType.STATUS_CHANGE:
            self.handle_children_status_change()
        elif command.type == CommandType.STOP_SIMULATON:
            self.handle_stop_simulation()
