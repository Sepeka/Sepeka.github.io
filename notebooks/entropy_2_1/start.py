"""Serve an automatically executed lesson plus a separate local code editor."""
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
os.chdir(root)
os.environ['_MARIMO_CONFIG_OVERLOAD_RUNTIME_AUTO_INSTANTIATE'] = 'true'
common = [str(root / 'entropy_2_1.py'), '--host', '127.0.0.1', '--no-token']
editor = subprocess.Popen([sys.executable, '-m', 'marimo', 'edit', *common,
                           '--port', '2720', '--headless', '--skip-update-check'])
try:
    viewer = subprocess.Popen([sys.executable, '-m', 'marimo', 'run', *common,
                               '--port', '2718', *[a for a in sys.argv[1:] if a != '--no-token']])
    try:
        viewer.wait()
    finally:
        viewer.terminate()
        viewer.wait()
finally:
    editor.terminate()
    editor.wait()
