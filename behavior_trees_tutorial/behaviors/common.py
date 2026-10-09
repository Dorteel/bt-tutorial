"""Small ROS-independent py_trees leaves."""
import py_trees as pt

Status = pt.common.Status


class Function(pt.behaviour.Behaviour):
    """Adapt an explicit status-returning function to a library leaf."""

    def __init__(self, name, function):
        super().__init__(name)
        self.function = function

    def update(self):
        return self.function()


class CountTicks(pt.behaviour.Behaviour):
    """An action that completes on its nth tick, restarting after termination."""

    def __init__(self, name, ticks=3):
        super().__init__(name)
        if ticks < 1:
            raise ValueError("ticks must be positive")
        self.ticks = ticks
        self.count = 0
        self.events = []

    def setup(self, **kwargs):
        self.events.append("setup")

    def initialise(self):
        self.count = 0
        self.events.append("initialise")

    def update(self):
        self.count += 1
        self.events.append(f"update {self.count}")
        return Status.SUCCESS if self.count >= self.ticks else Status.RUNNING

    def terminate(self, new_status):
        self.events.append(f"terminate {new_status.name}")
