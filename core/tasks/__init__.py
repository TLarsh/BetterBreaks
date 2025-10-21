import importlib
import os
from pathlib import Path

task_dir = Path(__file__).resolve().parent

for file in os.listdir(task_dir):
    if file.endswith('.py') and file != '__init__.py':
        module_name = f"core.tasks.{file[:-3]}"
        importlib.import_module(module_name)
