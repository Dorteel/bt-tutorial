from glob import glob
from setuptools import find_packages, setup

package_name = "behavior_trees_tutorial"
setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["tests"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml", "README.md", "notes.md"]),
        ("share/" + package_name + "/launch", glob("launch/*.launch.py")),
        ("share/" + package_name + "/config", glob("config/*.yaml")),
        ("share/" + package_name + "/notebooks", glob("notebooks/*.ipynb")),
        ("share/" + package_name + "/exercises", ["exercises/README.md"]),
        ("share/" + package_name + "/solutions", ["solutions/README.md"]),
    ],
    install_requires=["setuptools", "py_trees>=2.3,<3"],
    extras_require={"notebooks": ["jupyterlab", "nbclient", "graphviz", "ipywidgets"],
                    "test": ["pytest", "nbformat", "nbclient", "graphviz", "ipywidgets", "ipykernel"]},
    zip_safe=False,
    maintainer="Behavior Trees Tutorial contributors",
    maintainer_email="maintainers@example.com",
    description="Behavior trees from first principles to ROS 2 Jazzy robotics",
    license="MIT",
    entry_points={"console_scripts": [
        "standalone_robot = behavior_trees_tutorial.simulations.robot:main",
        "minimal_tree = behavior_trees_tutorial.ros_nodes.executables:minimal_main",
        "simulated_robot = behavior_trees_tutorial.ros_nodes.executables:robot_main",
        "simulated_action_server = behavior_trees_tutorial.ros_nodes.executables:action_main",
        "robot_tree = behavior_trees_tutorial.ros_nodes.executables:tree_main",
    ]},
)
