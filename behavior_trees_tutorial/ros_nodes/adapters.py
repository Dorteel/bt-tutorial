"""Nonblocking BT leaves: callbacks progress in the executor between ticks."""
from time import monotonic
import py_trees as pt
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from example_interfaces.action import Fibonacci
from std_srvs.srv import Trigger

Status = pt.common.Status


class ServiceCall(pt.behaviour.Behaviour):
    """Trigger is appropriate for these tiny, argument-free simulated operations."""

    def __init__(self, name, node, service, timeout=2.0):
        super().__init__(name)
        self.client = node.create_client(Trigger, service)
        self.timeout = timeout
        self.future = None

    def initialise(self):
        self.deadline = monotonic() + self.timeout
        self.future = None

    def update(self):
        if monotonic() >= self.deadline:
            return Status.FAILURE
        if self.future is None:
            if not self.client.service_is_ready():
                return Status.RUNNING
            self.future = self.client.call_async(Trigger.Request())
        if not self.future.done():
            return Status.RUNNING
        try:
            return Status.SUCCESS if self.future.result().success else Status.FAILURE
        except Exception:
            return Status.FAILURE

    def terminate(self, new_status):
        if self.future is not None and not self.future.done():
            # Removing a local request does NOT undo the server's side effect.
            self.client.remove_pending_request(self.future)


class FibonacciAction(pt.behaviour.Behaviour):
    """A cancellable long-running action with a total wall-clock deadline."""

    def __init__(self, name, node, action="compute", order=6, timeout=3.0):
        super().__init__(name)
        self.client = ActionClient(node, Fibonacci, action)
        self.order, self.timeout = order, timeout
        self.goal_future = None
        self.result_future = None
        self.cancel_future = None
        self.feedback = []

    def initialise(self):
        self.deadline = monotonic() + self.timeout
        self.goal_future = self.result_future = self.cancel_future = None
        self.feedback = []

    def update(self):
        if monotonic() >= self.deadline:
            self.feedback_message = "deadline exceeded"
            return Status.FAILURE
        if self.goal_future is None:
            if not self.client.server_is_ready():
                return Status.RUNNING
            self.goal_future = self.client.send_goal_async(
                Fibonacci.Goal(order=self.order),
                feedback_callback=lambda message: self.feedback.append(list(message.feedback.sequence)),
            )
        try:
            if not self.goal_future.done():
                return Status.RUNNING
            goal = self.goal_future.result()
            if not goal.accepted:
                return Status.FAILURE
            if self.result_future is None:
                self.result_future = goal.get_result_async()
            if not self.result_future.done():
                return Status.RUNNING
            result = self.result_future.result()
            return (Status.SUCCESS if result.status == GoalStatus.STATUS_SUCCEEDED
                    else Status.FAILURE)
        except Exception as error:
            self.feedback_message = str(error)
            return Status.FAILURE

    def terminate(self, new_status):
        if self.goal_future is None:
            return
        if self.result_future is not None and self.result_future.done():
            return
        # Capture this request: a subsequent initialise may start another one.
        # Cancelling before acceptance must still cancel the eventual accepted goal.
        def cancel_when_accepted(future):
            try:
                goal = future.result()
                if goal.accepted:
                    self.cancel_future = goal.cancel_goal_async()
            except Exception as error:
                self.feedback_message = f"cancel failed: {error}"
        self.goal_future.add_done_callback(cancel_when_accepted)

    def shutdown(self):
        self.client.destroy()
