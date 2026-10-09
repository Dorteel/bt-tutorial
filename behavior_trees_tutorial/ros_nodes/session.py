"""One owner for a notebook's ROS context, executor, nodes, and spin thread."""
from threading import Thread
from time import monotonic, sleep
import rclpy
from rclpy.context import Context
from rclpy.executors import MultiThreadedExecutor


class RosSession:
    def __enter__(self):
        self.context = Context()
        rclpy.init(args=[], context=self.context)
        self.executor = MultiThreadedExecutor(num_threads=4, context=self.context)
        self.nodes = []
        self.error = None
        self.thread = Thread(target=self._spin, daemon=True)
        self.thread.start()
        return self

    def _spin(self):
        try:
            self.executor.spin()
        except Exception as error:
            self.error = error

    def add(self, node):
        self.nodes.append(node)
        self.executor.add_node(node)
        return node

    def node(self, name, **kwargs):
        return self.add(rclpy.create_node(name, context=self.context, **kwargs))

    def wait(self, predicate, timeout=5.0):
        deadline = monotonic() + timeout
        while not predicate():
            if self.error is not None:
                raise RuntimeError("ROS executor failed") from self.error
            if monotonic() >= deadline:
                raise TimeoutError("ROS operation did not finish before its deadline")
            sleep(0.01)

    def __exit__(self, exc_type, exc, traceback):
        # Finish callbacks before destroying entities they may still use.
        self.executor.shutdown()
        self.thread.join()
        for node in reversed(self.nodes):
            node.destroy_node()
        self.context.try_shutdown()
        if exc_type is None and self.error is not None:
            raise RuntimeError("ROS executor failed") from self.error
