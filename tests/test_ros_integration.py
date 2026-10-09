"""Opt in with TUTORIAL_TEST_ROS=1 in a sourced Jazzy environment."""
import os
from time import monotonic, sleep
from dataclasses import asdict
from uuid import uuid4
import pytest

pytestmark = [pytest.mark.ros, pytest.mark.skipif(
    os.environ.get('TUTORIAL_TEST_ROS') != '1', reason='Set TUTORIAL_TEST_ROS=1 to run live ROS tests')]


def run(root):
    import py_trees as pt
    deadline = monotonic() + 7
    while monotonic() < deadline:
        root.tick_once()
        if root.status is not pt.common.Status.RUNNING:
            return root.status
        sleep(0.01)
    root.stop(pt.common.Status.INVALID)
    raise TimeoutError('tree did not terminate')


def test_context_cleanup_on_error_and_rerun():
    from behavior_trees_tutorial.ros_nodes.session import RosSession
    for _ in range(2):
        with pytest.raises(ValueError, match='intentional'):
            with RosSession() as ros:
                ros.node('cleanup_test')
                raise ValueError('intentional')
        assert not ros.context.ok() and not ros.thread.is_alive()


def test_distributed_mission_matches_local():
    import py_trees as pt
    from behavior_trees_tutorial.ros_nodes.session import RosSession
    from behavior_trees_tutorial.ros_nodes.servers import RobotServer
    from behavior_trees_tutorial.ros_nodes.robot_tree import create_mission
    from behavior_trees_tutorial.simulations.robot import World, mission
    with RosSession() as ros:
        namespace = '/test_' + uuid4().hex
        server = ros.add(RobotServer(context=ros.context, namespace=namespace))
        node = ros.node('tree', namespace=namespace)
        root = create_mission(node)
        assert run(root) is pt.common.Status.SUCCESS
        local = World()
        mission(local).tick_once()
        assert asdict(local) == asdict(server.world)


@pytest.mark.parametrize('mode', ['success', 'rejection', 'timeout', 'early_cancel'])
def test_action_protocol(mode):
    import py_trees as pt
    from behavior_trees_tutorial.ros_nodes.session import RosSession
    from behavior_trees_tutorial.ros_nodes.servers import FibonacciServer
    from behavior_trees_tutorial.ros_nodes.adapters import FibonacciAction
    with RosSession() as ros:
        namespace = '/action_test_' + uuid4().hex
        server = ros.add(FibonacciServer(context=ros.context, namespace=namespace))
        node = ros.node('tree', namespace=namespace)
        action = FibonacciAction('work', node, order=0 if mode == 'rejection' else 20,
                                 timeout=0.1 if mode == 'timeout' else 4.0)
        try:
            ros.wait(action.client.server_is_ready)
            if mode == 'early_cancel':
                action.tick_once()
                action.stop(pt.common.Status.INVALID)
                ros.wait(lambda: server.cancelled == 1)
            else:
                expected = pt.common.Status.SUCCESS if mode == 'success' else pt.common.Status.FAILURE
                assert run(action) is expected
                if mode == 'timeout':
                    ros.wait(lambda: server.cancelled == 1)
            ros.wait(lambda: not server.busy)
        finally:
            action.stop(pt.common.Status.INVALID)
            ros.wait(lambda: not server.busy)
            action.shutdown()


def test_missing_service_has_bounded_failure():
    import py_trees as pt
    from behavior_trees_tutorial.ros_nodes.session import RosSession
    from behavior_trees_tutorial.ros_nodes.adapters import ServiceCall
    with RosSession() as ros:
        node = ros.node('missing_service_test')
        root = ServiceCall('missing', node, '/missing_' + uuid4().hex, timeout=0.1)
        assert run(root) is pt.common.Status.FAILURE
