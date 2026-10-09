"""ROS CLI entry points. Tick callbacks never block on ROS futures."""
import rclpy
from rclpy.executors import MultiThreadedExecutor
import py_trees as pt
import py_trees_ros
from behavior_trees_tutorial.behaviors.common import CountTicks
from behavior_trees_tutorial.ros_nodes.servers import RobotServer, FibonacciServer
from behavior_trees_tutorial.ros_nodes.robot_tree import create_mission


def spin_server(factory):
    rclpy.init()
    node = factory()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.try_shutdown()


def robot_main():
    spin_server(RobotServer)


def action_main():
    spin_server(FibonacciServer)


def run_tree(factory, name):
    rclpy.init()
    node = rclpy.create_node(name)
    period = node.declare_parameter("tick_period", 0.05).value
    tree = py_trees_ros.trees.BehaviourTree(factory(node))
    executor = rclpy.executors.SingleThreadedExecutor()
    executor.add_node(node)
    try:
        tree.setup(node=node, timeout=5.0)
        if period <= 0:
            raise ValueError("tick_period must be positive")
        tree.tick_tock(period_ms=period * 1000)
        while rclpy.ok() and tree.root.status not in (
            pt.common.Status.SUCCESS, pt.common.Status.FAILURE
        ):
            executor.spin_once(timeout_sec=0.1)
        node.get_logger().info(f"Mission: {tree.root.status.name}")
        failed = tree.root.status == pt.common.Status.FAILURE
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        failed = False
    finally:
        tree.interrupt()
        tree.root.stop(pt.common.Status.INVALID)
        executor.shutdown()
        tree.shutdown(destroy_node=False)
        node.destroy_node()
        rclpy.try_shutdown()
    if failed:
        raise SystemExit(1)


def minimal_main():
    run_tree(lambda node: CountTicks("Work", ticks=3), "minimal_tree")


def tree_main():
    run_tree(create_mission, "robot_tree")
