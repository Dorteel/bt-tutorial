"""A world small enough to reason about; no ROS or simulator dependency."""
from dataclasses import dataclass, asdict
import py_trees as pt
from behavior_trees_tutorial.behaviors.common import Function, Status


@dataclass
class World:
    location: str = "home"
    detected: bool = False
    holding: bool = False
    delivered: bool = False
    blocked: bool = True

    def navigate(self):
        if self.blocked:
            return False
        self.location = "table"
        return True

    def clear(self):
        self.blocked = False
        return True

    def detect(self):
        self.detected = self.location == "table"
        return self.detected

    def pick(self):
        if not self.detected or self.location != "table":
            return False
        self.holding = True
        return True

    def place(self):
        if not self.holding:
            return False
        self.holding, self.delivered = False, True
        return True


def leaf(name, operation):
    return Function(name, lambda: Status.SUCCESS if operation() else Status.FAILURE)


def mission(world, make_leaf=leaf):
    """The same mission topology can use local functions or ROS adapters."""
    navigation = pt.composites.Selector("Reach table", memory=True, children=[
        make_leaf("Navigate", world.navigate),
        pt.composites.Sequence("Clear and retry", memory=True, children=[
            make_leaf("Clear obstacle", world.clear),
            make_leaf("Navigate again", world.navigate),
        ]),
    ])
    return pt.composites.Sequence("Deliver object", memory=True, children=[
        navigation, make_leaf("Detect", world.detect),
        make_leaf("Pick", world.pick), make_leaf("Place", world.place),
    ])


def main():
    world = World()
    root = mission(world)
    root.tick_once()
    print(root.status.name, asdict(world))
