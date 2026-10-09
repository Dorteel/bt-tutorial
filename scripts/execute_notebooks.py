#!/usr/bin/env python3
"""Execute notebooks in fresh kernels, from a directory outside the checkout."""
import argparse
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import json
import nbformat
from nbclient import NotebookClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=['standalone', 'ros', 'all'], default='standalone')
    parser.add_argument('--lessons', type=int, nargs='+', help='Optionally select lesson numbers')
    parser.add_argument('--in-place', action='store_true', help='Save verified outputs into source notebooks')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    notebooks = sorted((root / 'notebooks').glob('*.ipynb'))
    with TemporaryDirectory(prefix='bt-notebooks-') as directory:
        temporary = Path(directory)
        kernel = temporary / 'kernels' / 'bt-validation'
        kernel.mkdir(parents=True)
        (kernel / 'kernel.json').write_text(json.dumps({
            'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
            'display_name': 'BT validation', 'language': 'python',
        }))
        os.environ['JUPYTER_PATH'] = str(temporary) + os.pathsep + os.environ.get('JUPYTER_PATH', '')
        count = 0
        for path in notebooks:
            notebook = nbformat.read(path, as_version=4)
            if args.lessons and notebook.metadata.tutorial.lesson not in args.lessons:
                continue
            ros = notebook.metadata.tutorial.requires_ros
            if args.group == 'standalone' and ros or args.group == 'ros' and not ros:
                continue
            nbformat.validate(notebook)
            # Prove the first sixteen notebooks cannot import ROS, even on a ROS host.
            guard = nbformat.v4.new_code_cell('''
import sys
import importlib.abc
class NoROS(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'rclpy', 'py_trees_ros', 'std_msgs', 'std_srvs', 'example_interfaces'}:
            raise ImportError('ROS is forbidden in standalone lessons: ' + fullname)
sys.meta_path.insert(0, NoROS())
''')
            if not ros:
                notebook.cells.insert(0, guard)
            print(f'Executing {path.name}', flush=True)
            NotebookClient(notebook, timeout=90, kernel_name='bt-validation',
                           resources={'metadata': {'path': directory}}).execute()
            if not ros:
                notebook.cells.pop(0)
            # Each lesson must actually produce a rendered Graphviz SVG, not just a repr.
            assert any('image/svg+xml' in output.get('data', {})
                       for cell in notebook.cells for output in cell.get('outputs', [])), path
            if args.in_place:
                nbformat.write(notebook, path)
            count += 1
        print(f'Passed: {count} notebooks', flush=True)


if __name__ == '__main__':
    main()
