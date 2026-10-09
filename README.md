# Behavior Trees Tutorial

Twenty executable Jupyter lessons, from a function returning a status to a small ROS 2 robot.
The first sixteen lessons run without ROS. The final four introduce ROS only after the
behavior-tree concepts they support are familiar.

Target: **Ubuntu 24.04 · Python 3.12 · ROS 2 Jazzy · ament_python · colcon**.
The repository directory may be named `bt-tutorial`; the ROS package and Python import are
both named `behavior_trees_tutorial`.

## Start without ROS

From this checkout:

```bash
sudo apt install python3-venv graphviz
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[notebooks,test]'
python -m ipykernel install --user --name bt-standalone --display-name 'BT tutorial (standalone)'
python -m jupyterlab notebooks
```

Select **BT tutorial (standalone)** in Jupyter. Start with `01_introduction.ipynb`.
Editable installation makes imports work from any directory; no `sys.path` edits are used.
Graphviz's `dot` executable renders the diagrams. The Python `graphviz` package alone is
not enough. JupyterLab supports the included ipywidgets controls.

Each notebook is independent: use **Restart Kernel and Run All**. Tick/Reset buttons drive
local examples without background timers. Some sliders change observations; some rebuild
fresh state, as explained in the cell. ROS notebooks keep widgets local and release ROS
resources before displaying controls.

## Build and run with ROS 2 Jazzy

Install ROS 2 Jazzy first using the [official Ubuntu instructions](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html).
Place this checkout under a workspace's `src/` directory, then from the workspace root:

```bash
source /opt/ros/jazzy/setup.bash
sudo apt install python3-colcon-common-extensions python3-rosdep python3-venv graphviz
# If rosdep has never been initialized on this machine:
# sudo rosdep init
rosdep update
rosdep install --from-paths src --ignore-src -r -y --rosdistro jazzy
colcon build --packages-select behavior_trees_tutorial
source install/setup.bash

ros2 run behavior_trees_tutorial standalone_robot
ros2 run behavior_trees_tutorial minimal_tree
ros2 launch behavior_trees_tutorial minimal.launch.py
ros2 launch behavior_trees_tutorial robot.launch.py
```

The ROS dependency `py_trees_ros` resolves to `ros-jazzy-py-trees-ros`. The integration was
checked against Jazzy's **py_trees_ros 2.6.0 and py_trees 2.6.0**, including its supplied-node
setup and `shutdown(destroy_node=False)` API. Use Jazzy packages together; do not mix ROS 1
examples or another ROS distribution into this environment.

`robot.launch.py` runs a simulated world and the mission controller in separate processes.
The first navigation attempt fails because the route is blocked. Recovery clears it, then
the robot navigates, detects an object, picks it up, and places it in a tray. The controller
prints `Mission: SUCCESS` and the launch shuts down. A failed mission returns exit code 1
from `robot_tree`; ROS launch itself may still return 0 after shutting its processes down.
See process output when diagnosing a failed launch.

For manual operation, keep one sourced terminal running the server:

```bash
ros2 run behavior_trees_tutorial simulated_robot
```

In other sourced terminals:

```bash
ros2 topic echo /robot/state
ros2 run behavior_trees_tutorial robot_tree
```

The independent arithmetic action example has its own executable:

```bash
ros2 run behavior_trees_tutorial simulated_action_server
ros2 action send_goal /compute example_interfaces/action/Fibonacci '{order: 6}' --feedback
```

The action server stays alive until Ctrl-C. It deliberately slows computation to make feedback
and cancellation observable. It is not a navigation server. Run one default-namespaced copy
of each example at a time. Notebook examples use unique namespaces to avoid collisions.
Configuration defaults live in [config/tutorial.yaml](config/tutorial.yaml).

## Jupyter in the ROS workspace

Use Ubuntu's Python 3.12, whose ABI matches Jazzy. Avoid an unrelated Conda Python.
From the workspace root, in a new terminal:

```bash
source /opt/ros/jazzy/setup.bash
python3 -m venv --system-site-packages .venv-ros
touch .venv-ros/COLCON_IGNORE
source .venv-ros/bin/activate
python -m pip install jupyterlab nbclient graphviz ipywidgets pytest
source install/setup.bash
python -m ipykernel install --user --name bt-ros --display-name 'BT tutorial (ROS 2 Jazzy)'
python -m jupyterlab
```

Navigate to this checkout's `notebooks/` and select **BT tutorial (ROS 2 Jazzy)**. Launch
Jupyter from this sourced terminal every time: a kernelspec remembers the Python executable,
not the shell's ROS environment. No editable installation is required after sourcing the
built workspace. Rebuild after changing installed Python files, or use `colcon build
--symlink-install --packages-select behavior_trees_tutorial` during development.

`RosSession` owns a fresh context, executor, spin thread, and nodes for each `with` block.
Normal completion and exceptions both clean up. A notebook never spins a node already owned
by that session. Actions are canceled and allowed to finish cancellation before their clients
are destroyed. Interrupt a running cell normally and allow its `finally` block to complete;
force-killing a kernel cannot execute Python cleanup.

## Learning path

| Lessons | Focus |
|---|---|
| [01](notebooks/01_introduction.ipynb)–[05](notebooks/05_ticking.ipynb) | Statuses, a tiny engine, sequences, selectors, ticking |
| [06](notebooks/06_py_trees.ipynb)–[10](notebooks/10_blackboard.ipynb) | py_trees, lifecycle, decorators, parallel policies, blackboards |
| [11](notebooks/11_reactivity.ipynb)–[13](notebooks/13_design_patterns.ipynb) | Preemption, recovery, hierarchical design |
| [14](notebooks/14_simulated_robot.ipynb)–[16](notebooks/16_autonomous_agents.ipynb) | Robot simulation, symbolic planning, validated agent tools |
| [17](notebooks/17_ros2_introduction.ipynb) | Nodes, topics, services, actions, executors |
| [18](notebooks/18_ros2_behavior_trees.ipynb) | py_trees_ros, timer ticks, blackboard observations, lifecycle |
| [19](notebooks/19_ros2_actions.ipynb) | Asynchronous actions, feedback, cancellation, deadlines, recovery |
| [20](notebooks/20_ros2_robot_example.ipynb) | A distributed simulated robot and standalone equivalence |

Every notebook includes learning objectives, intuition, an executable example, implementation
steps, interaction, observations, exercises, and a summary. Status colors are green for
SUCCESS, red for FAILURE, yellow for RUNNING, and gray for inactive/INVALID. A node's displayed
status is its last lifecycle state, not a claim that its callback is running on another thread.
Exercise hints and worked answers are in [exercises](exercises/README.md) and
[solutions](solutions/README.md). Architectural choices and verification evidence are in
[notes.md](notes.md).

## Verification

From the checkout with the relevant Python environment active:

```bash
python -m pytest -q
python scripts/execute_notebooks.py --group standalone
```

The notebook runner creates a fresh kernel for each notebook, uses the active Python,
executes from a temporary directory outside the checkout, blocks ROS imports for lessons
1–16, and checks that Graphviz SVGs actually rendered. Add `--in-place` to save verified
outputs. The standard test run skips live ROS tests unless explicitly enabled.

In the sourced ROS notebook environment:

```bash
TUTORIAL_TEST_ROS=1 python -m pytest -q
python scripts/execute_notebooks.py --group ros
python scripts/check_ros_install.py
```

From the workspace root:

```bash
colcon test --packages-select behavior_trees_tutorial --event-handlers console_direct+
colcon test-result --verbose
```

Live ROS tests need local DDS communication. They cover a distributed mission, clean reruns,
missing-service deadlines, accepted and rejected actions, timeout cancellation, and
cancellation before goal acceptance. Standalone tests compare the tiny engine and py_trees
across status combinations and exercise widget Tick/Reset callbacks.

## Package layout

- `behavior_trees_tutorial/trees`: ROS-free teaching engine.
- `behaviors`: ROS-free py_trees leaves.
- `simulations`: world model, mission factory, and symbolic planner.
- `ros_nodes`: communication adapters, simulated servers, resource ownership, CLI entry points.
- `notebooks`: all twenty lessons, also installed under the package share directory.
- `launch`, `config`, `resource`, `package.xml`, `setup.py`, `setup.cfg`: ament package integration.
- `tests`, `scripts`: semantic tests, live integration checks, notebook execution.

The MIT license applies to this tutorial; dependencies retain their own licenses.
