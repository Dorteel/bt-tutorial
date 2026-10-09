from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package="behavior_trees_tutorial", executable="minimal_tree", output="screen")
    ])
