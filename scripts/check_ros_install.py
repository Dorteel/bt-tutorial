#!/usr/bin/env python3
"""Smoke-test installed executables and launches in a sourced ROS workspace."""
import os
import signal
import subprocess
from tempfile import TemporaryFile
import time

PACKAGE = 'behavior_trees_tutorial'


def run(*arguments, expected=None):
    result = subprocess.run(arguments, text=True, capture_output=True, timeout=20)
    output = result.stdout + result.stderr
    print(output, end='', flush=True)
    assert result.returncode == 0, (arguments, result.returncode)
    if expected is not None:
        assert expected in output, (arguments, expected)
    return output


def main():
    run('ros2', 'run', PACKAGE, 'standalone_robot', expected='SUCCESS')
    run('ros2', 'run', PACKAGE, 'minimal_tree', expected='Mission: SUCCESS')
    run('ros2', 'launch', PACKAGE, 'minimal.launch.py', expected='Mission: SUCCESS')
    output = run('ros2', 'launch', PACKAGE, 'robot.launch.py', expected='Mission: SUCCESS')
    assert 'process has died' not in output
    # A separate process exercises the actual console entry point and action transport.
    with TemporaryFile(mode='w+') as log:
        server = subprocess.Popen(['ros2', 'run', PACKAGE, 'simulated_action_server'],
                                  stdout=log, stderr=log, start_new_session=True)
        try:
            time.sleep(0.3)
            assert server.poll() is None, 'Action server exited during startup'
            run('ros2', 'action', 'send_goal', '/compute',
                'example_interfaces/action/Fibonacci', '{order: 6}', '--feedback',
                expected='SUCCEEDED')
        finally:
            if server.poll() is None:
                os.killpg(server.pid, signal.SIGINT)
                try:
                    server.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(server.pid, signal.SIGKILL)
                    server.wait()
                    raise
            log.seek(0)
            output = log.read()
            print(output, end='')
            assert 'Traceback' not in output, output
    print('Passed: all five entry points and both launch files')


if __name__ == '__main__':
    main()
