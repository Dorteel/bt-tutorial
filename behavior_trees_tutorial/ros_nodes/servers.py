"""Lightweight ROS simulations using existing interfaces."""
from dataclasses import asdict
import json
from time import sleep
from threading import Lock
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from example_interfaces.action import Fibonacci
from std_msgs.msg import String
from std_srvs.srv import Trigger
from behavior_trees_tutorial.simulations.robot import World


class RobotServer(Node):
    def __init__(self, **kwargs):
        super().__init__("simulated_robot", **kwargs)
        self.world = World(blocked=self.declare_parameter("blocked", True).value)
        self.publisher = self.create_publisher(String, "robot/state", 10)
        self.operation_services = []
        for operation in ["navigate", "clear", "detect", "pick", "place"]:
            def callback(request, response, operation=operation):
                response.success = getattr(self.world, operation)()
                response.message = json.dumps(asdict(self.world))
                self.publish_state()
                return response
            self.operation_services.append(self.create_service(Trigger, f"robot/{operation}", callback))
        self.timer = self.create_timer(0.1, self.publish_state)

    def publish_state(self):
        self.publisher.publish(String(data=json.dumps(asdict(self.world))))


class FibonacciServer(Node):
    """Deliberately slow Fibonacci, so RUNNING, feedback, and cancel are visible."""

    def __init__(self, **kwargs):
        super().__init__("simulated_action_server", **kwargs)
        self.delay = self.declare_parameter("step_seconds", 0.04).value
        if not 0 < self.delay <= 0.1:
            raise ValueError("step_seconds must be in (0, 0.1]")
        self.cancelled = 0
        self.completed = 0
        self.busy = False
        self.lock = Lock()
        self.server = ActionServer(
            self, Fibonacci, "compute", self.execute,
            callback_group=ReentrantCallbackGroup(),
            goal_callback=self.accept,
            cancel_callback=lambda goal: CancelResponse.ACCEPT,
        )

    def accept(self, request):
        with self.lock:
            if self.busy or not 1 <= request.order <= 20:
                return GoalResponse.REJECT
            self.busy = True
            return GoalResponse.ACCEPT

    def execute(self, goal):
        sequence = [0, 1]
        try:
            for _ in range(goal.request.order):
                sleep(self.delay)  # Only the simulated worker blocks, never a BT tick.
                if goal.is_cancel_requested:
                    goal.canceled()
                    self.cancelled += 1
                    return Fibonacci.Result(sequence=sequence)
                sequence.append(sequence[-1] + sequence[-2])
                goal.publish_feedback(Fibonacci.Feedback(sequence=sequence))
            goal.succeed()
            self.completed += 1
            return Fibonacci.Result(sequence=sequence)
        finally:
            with self.lock:
                self.busy = False

    def destroy_node(self):
        self.server.destroy()
        return super().destroy_node()
