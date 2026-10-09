"""Check semantics at boundaries, not implementation details."""
from itertools import product
import sys
import subprocess
import py_trees as pt
import pytest
from behavior_trees_tutorial.trees.core import Action, Sequence, Selector, Status
from behavior_trees_tutorial.behaviors.common import CountTicks
from behavior_trees_tutorial.simulations.robot import World, mission
from behavior_trees_tutorial.simulations.planning import Operator, plan


@pytest.mark.parametrize('kind', ['sequence', 'selector'])
@pytest.mark.parametrize('statuses', list(product(['SUCCESS', 'FAILURE', 'RUNNING'], repeat=2)))
def test_library_matches_teaching_engine(kind, statuses):
    simple_type = Sequence if kind == 'sequence' else Selector
    library_type = pt.composites.Sequence if kind == 'sequence' else pt.composites.Selector
    simple = simple_type('root', [Action(str(i), lambda s=s: Status[s]) for i, s in enumerate(statuses)])
    leaves = {'SUCCESS': pt.behaviours.Success, 'FAILURE': pt.behaviours.Failure,
              'RUNNING': pt.behaviours.Running}
    library = library_type('root', memory=False,
                           children=[leaves[s](str(i)) for i, s in enumerate(statuses)])
    simple.tick()
    library.tick_once()
    assert simple.status.name == library.status.name
    assert [x.status.name for x in simple.children] == [x.status.name for x in library.children]


@pytest.mark.parametrize('memory, expected', [(False, Status.FAILURE), (True, Status.RUNNING)])
def test_memory_changes_guard_rechecking(memory, expected):
    state = {'safe': True}
    root = Sequence('root', [Action('guard', lambda: Status.SUCCESS if state['safe'] else Status.FAILURE),
                             Action('work', lambda: Status.RUNNING)], memory=memory)
    root.tick()
    state['safe'] = False
    assert root.tick() is expected


def test_preemption_calls_termination():
    state = {'urgent': False}
    from behavior_trees_tutorial.behaviors.common import Function
    work = CountTicks('work', 5)
    root = pt.composites.Selector('root', memory=False, children=[
        Function('urgent', lambda: pt.common.Status.SUCCESS if state['urgent'] else pt.common.Status.FAILURE), work])
    root.tick_once()
    state['urgent'] = True
    root.tick_once()
    assert work.status is pt.common.Status.INVALID
    assert work.events[-1] == 'terminate INVALID'


@pytest.mark.parametrize('blocked', [True, False])
def test_robot_delivery(blocked):
    world = World(blocked=blocked)
    tree = mission(world)
    tree.tick_once()
    assert tree.status is pt.common.Status.SUCCESS
    assert world.delivered and not world.holding and world.location == 'table'
    assert not world.blocked


def test_robot_preconditions():
    world = World()
    assert not world.pick() and not world.place() and not world.detect()
    assert not world.navigate()


def test_planner_unreachable_and_already_achieved():
    operator = Operator('pick', frozenset({'object'}), frozenset({'holding'}))
    assert plan(set(), {'holding'}, [operator]) is None
    assert plan({'holding'}, {'holding'}, [operator]) == []
    assert plan({'object'}, {'holding'}, [operator]) == [operator]


def test_package_import_does_not_import_ros():
    subprocess.run([sys.executable, '-c',
                    'import behavior_trees_tutorial; import sys; '
                    'assert "rclpy" not in sys.modules; assert "py_trees_ros" not in sys.modules'], check=True)


def test_widget_tick_and_reset_callbacks():
    from behavior_trees_tutorial.visualization import playground
    created = []
    def factory():
        root = CountTicks('work', ticks=2)
        created.append(root)
        return root
    widget = playground(factory)
    buttons = widget.children[0].children
    buttons[0].click()
    assert created[-1].status is pt.common.Status.RUNNING
    buttons[1].click()
    assert len(created) == 2 and created[0].status is pt.common.Status.INVALID
    assert created[-1].status is pt.common.Status.INVALID
    widget.close()
