"""A deliberately small teaching engine, not a replacement for py_trees."""
from enum import Enum, auto


class Status(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()
    INVALID = auto()  # Not visited, or interrupted; never returned by an action.


class Action:
    """A named function that can be ticked."""

    def __init__(self, name, function):
        self.name = name
        self.function = function
        self.status = Status.INVALID
        self.children = []

    def tick(self):
        self.status = self.function()
        return self.status

    def reset(self):
        self.status = Status.INVALID


class Sequence:
    """Stop at the first child that does not succeed."""

    def __init__(self, name, children, memory=False):
        self.name, self.children, self.memory = name, children, memory
        self.status = Status.INVALID
        self.index = 0

    def tick(self):
        start = self.index if self.memory and self.status is Status.RUNNING else 0
        for index in range(start, len(self.children)):
            result = self.children[index].tick()
            if result is not Status.SUCCESS:
                for child in self.children[index + 1:]:
                    child.reset()
                self.index, self.status = index, result
                return result
        self.status = Status.SUCCESS
        return self.status

    def reset(self):
        self.status, self.index = Status.INVALID, 0
        for child in self.children:
            child.reset()


class Selector(Sequence):
    """Stop at the first child that does not fail."""

    def tick(self):
        start = self.index if self.memory and self.status is Status.RUNNING else 0
        for index in range(start, len(self.children)):
            result = self.children[index].tick()
            if result is not Status.FAILURE:
                for child in self.children[index + 1:]:
                    child.reset()
                self.index, self.status = index, result
                return result
        self.status = Status.FAILURE
        return self.status
