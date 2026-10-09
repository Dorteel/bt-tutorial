"""One terminal starts the simulated robot and mission tree."""
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import EmitEvent, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch_ros.actions import Node


def generate_launch_description():
    config = str(Path(get_package_share_directory("behavior_trees_tutorial")) / "config/tutorial.yaml")
    def node(executable):
        return Node(package="behavior_trees_tutorial", executable=executable,
                    parameters=[config], output="screen")
    mission = node("robot_tree")
    return LaunchDescription([
        RegisterEventHandler(OnProcessExit(
            target_action=mission, on_exit=[EmitEvent(event=Shutdown(reason="Mission finished"))])),
        node("simulated_robot"), mission,
    ])
