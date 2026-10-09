# Design and verification notes

## Separation of concepts

The package root and all modules outside `ros_nodes` are ROS-independent. Lessons 1–5 use
ordinary Python and a tiny engine; lessons 6–16 introduce py_trees and applications without
rclpy. Graphviz and ipywidgets are notebook extras, not runtime ROS dependencies.
Importing the package root does not import either ROS or py_trees.

The teaching engine has only an Action, Sequence, Selector, and Status. It deliberately
omits resource ownership, general visitors, asynchronous work, and complete production
lifecycle semantics. Resetting its status does not cancel external work. Lesson 7 explains
why the maintained library's lifecycle hooks earn their existence. Selector reuses the
small composite state layout; no extensibility framework is added.

`Function` adapts explicit status-returning functions. `CountTicks` is a deterministic
stateful leaf, never described as a physical clock. A tick count and elapsed time are different
quantities. Graphviz traverses either engine through names, children, and status, preserving
a consistent visual vocabulary without introducing a rendering framework.

The examples expose source where a supporting module first becomes relevant. Notebook code
owns its own initial state. The shared modules avoid copying subtly different robot policies
across lessons. Interactive callbacks retain only local state, never live ROS clients.

## Robot and planning scope

The simulated robot teleports to a table. Picking and placing change flags; placing means
putting the object in a tray at that same table. There is no geometry, dynamics, or hardware.
Preconditions live in world operations, so erroneous ordering fails visibly.

A subtree factory accepts a leaf constructor. Standalone leaves call methods; ROS leaves
use those method names to select Trigger services. The same mission topology and final
world state can therefore be compared directly. ROS adds RUNNING ticks for communication;
it cannot be expected to have identical tick counts to instantaneous local functions.

The planner performs breadth-first search over immutable sets of facts. It illustrates
preconditions and effects, not full PDDL parsing or optimal planning with unequal costs.
Execution checks preconditions again and replans after an observed change. The agent lesson
uses deterministic mock proposals, an allowlist, argument validation, and bounded task size.
It does not require or call an LLM service.

## ROS interfaces and ownership

Short simulated world operations use std_srvs/Trigger. Telemetry uses std_msgs/String with
JSON for readability; it is explicitly not a recommended typed production state interface.
The cancellable long-running example uses example_interfaces/Fibonacci without redefining
its meaning as navigation. Real motion would use an appropriate domain action interface.
No custom messages are needed, so a pure ament_python package suffices.

Jazzy's packaged py_trees_ros 2.6.0 was inspected directly. The integration uses its
`setup(node=..., timeout=...)`, ROS `tick_tock`, and `shutdown(destroy_node=False)` methods.
The last option preserves the supplied node for its actual owner to destroy. We use ordinary
nodes and explicitly discuss managed lifecycle transitions rather than claiming to implement
a LifecycleNode application.

A RosSession owns a dedicated context, multithreaded executor, background spin thread, and
registered nodes. It shuts down the executor and joins it before destroying entities. All
simulated callbacks are bounded. ROS notebooks use unique namespaces and `with`/`finally`
blocks. They do not use global rclpy initialization, nested spins, or unowned background
threads. A crashed or force-killed process cannot promise Python finalization.

The tree timer and subscription in lesson 18 share the controller's default mutually
exclusive callback group. The simulated action worker uses a reentrant group and a bounded
sleep to let cancellation run in another executor thread. This is a teaching server, not a
scalable execution strategy. A lock prevents admission of overlapping action goals.

Action leaves start one goal per invocation and poll futures without blocking. Timeout
covers discovery, acceptance, and execution. Termination attaches a callback to the original
acceptance future so an early preemption still cancels an eventually accepted goal. Tests
exercise that race. Cancellation is asynchronous; examples wait for the simulated server
to become idle before destroying clients or moving to conflicting work. A production
controller needs an explicit stopped-state protocol and handles communication loss separately.
A service's local pending request can be removed, but its remote effects cannot be canceled.

## Dependency and packaging decisions

ament package metadata declares runtime ROS dependencies, launch, and configuration support.
Jupyter, widgets, and Graphviz Python bindings are optional pip extras. The system `dot`
binary is documented separately. Python metadata permits py_trees 2.x from 2.3; verification
currently covers 2.6.0. ROS integration targets the coherent Jazzy apt packages rather than
claiming compatibility with every earlier py_trees_ros release.

The ROS resource marker is installed into the ament index, executable scripts go into
`lib/behavior_trees_tutorial`, and launch/config/notebooks go into the package share directory.
The repository folder does not have to match the ROS package name. Normal users install
ROS dependencies with rosdep and build with colcon; standalone users install with pip.

## Verification record

The final implementation was verified on 2026-10-09:
The host has Ubuntu 24.04, Python 3.12, ROS 2 Jazzy, colcon, and Graphviz. To avoid modifying
the host ROS installation, additional Jazzy py_trees_ros and interface Debian packages were
extracted under `/tmp` for validation, and notebook Python dependencies were installed into
a temporary virtual environment. These paths are test infrastructure only; notebooks and
package code contain no hardcoded host paths.


| Check | Result |
|---|---|
| Standalone pytest | 27 passed; 7 ROS tests intentionally skipped |
| Full pytest with `TUTORIAL_TEST_ROS=1` | 34 passed |
| `colcon build --packages-select behavior_trees_tutorial` with isolated build/install bases | Passed |
| `colcon test` with live ROS tests enabled | 34 passed |
| `colcon test-result --verbose` | 0 errors, 0 failures, 0 skipped |
| Fresh-kernel standalone notebook execution with ROS imports blocked | 16/16 passed |
| Fresh-kernel ROS notebook execution | 4/4 passed |
| Graphviz SVG output in every notebook | 20/20 verified |
| Widget Tick and Reset callbacks | Passed |
| Installed ROS executable smoke checks | All five passed |
| Installed `minimal.launch.py` and `robot.launch.py` | Both completed successfully |
| Action CLI goal, feedback, result, and server Ctrl-C cleanup | Passed |

Notebook outputs are saved so diagrams and traces are visible before running a kernel.
The notebook runner executes outside the checkout, demonstrating that imports come from
installation rather than the current working directory. Tests found and corrected a
reserved rclpy Node attribute collision and a transient-status assumption in a memory
selector. The mission's recovery selector remembers its running branch so asynchronous
repair is not repeatedly displaced by another initial navigation request.

Graphviz rendering and widget callbacks were checked programmatically. No browser-driven
Jupyter UI test or physical robot validation was performed. The scope is the documented
lightweight simulation, not hardware safety, physics fidelity, or real-time guarantees.
