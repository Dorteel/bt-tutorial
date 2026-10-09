"""Keep mission decisions identical to the standalone implementation."""
from behavior_trees_tutorial.simulations.robot import World, mission
from behavior_trees_tutorial.ros_nodes.adapters import ServiceCall


def create_mission(node):
    def remote_leaf(name, operation):
        return ServiceCall(name, node, f"robot/{operation.__name__}")
    # World methods supply operation names only; state lives in RobotServer.
    return mission(World(), make_leaf=remote_leaf)
