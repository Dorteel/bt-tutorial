"""Notebook-only helpers. Importing the tutorial package needs no Jupyter."""
from graphviz import Digraph

COLORS = {"SUCCESS": "#a6dba0", "FAILURE": "#f4a3a3",
          "RUNNING": "#ffe082", "INVALID": "#dddddd"}


def diagram(root):
    """Render the current status of either teaching-engine or py_trees nodes."""
    graph = Digraph(graph_attr={"rankdir": "TB"})
    for node in walk(root):
        status = node.status.name
        graph.node(str(id(node)), f"{node.name}\n{status}", style="filled",
                   fillcolor=COLORS[status], shape="box")
        for child in node.children:
            graph.edge(str(id(node)), str(id(child)))
    return graph


def walk(root):
    yield root
    for child in root.children:
        yield from walk(child)


def tick(root):
    if hasattr(root, "tick_once"):
        root.tick_once()
    else:
        root.tick()
    return root.status.name


def trace(root, ticks):
    """Print each tick as a row, including inactive nodes."""
    rows = []
    for number in range(1, ticks + 1):
        tick(root)
        row = {node.name: node.status.name for node in walk(root)}
        rows.append(row)
        print(number, " | ".join(f"{name}: {status}" for name, status in row.items()))
    return rows


def playground(factory):
    """Factory returns fresh tree state. Buttons never start background timers."""
    import ipywidgets as widgets
    from IPython.display import display, clear_output

    root = factory()
    output = widgets.Output()
    advance = widgets.Button(description="Tick")
    reset = widgets.Button(description="Reset")

    def show():
        with output:
            clear_output(wait=True)
            display(diagram(root))

    def on_tick(_):
        tick(root)
        show()

    def on_reset(_):
        nonlocal root
        if hasattr(root, "stop"):
            import py_trees
            root.stop(py_trees.common.Status.INVALID)
        else:
            root.reset()
        root = factory()
        show()

    advance.on_click(on_tick)
    reset.on_click(on_reset)
    show()
    return widgets.VBox([widgets.HBox([advance, reset]), output])
