"""Tiny breadth-first symbolic planner: facts in, action names out."""
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class Operator:
    name: str
    requires: frozenset
    adds: frozenset
    deletes: frozenset = frozenset()

    def apply(self, facts):
        return (facts - self.deletes) | self.adds


def plan(initial, goal, operators):
    initial, goal = frozenset(initial), frozenset(goal)
    queue = deque([(initial, [])])
    visited = {initial}
    while queue:
        facts, steps = queue.popleft()
        if goal <= facts:
            return steps
        for operator in operators:
            if operator.requires <= facts:
                following = operator.apply(facts)
                if following not in visited:
                    visited.add(following)
                    queue.append((following, steps + [operator]))
    return None
