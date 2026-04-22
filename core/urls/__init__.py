import importlib
import os
from django.urls import include, path
from pathlib import Path


current_dir = Path(__file__).resolve().parent

urlpatterns = []


for file in os.listdir(current_dir):
    if file.endswith('_urls.py') and file != '__init__.py':
        module_name = f"core.urls.{file[:-3]}"  # Remove .py
        url_prefix = file.replace('_urls.py', '')  # E.g., 'auth', 'user'
        try:
            module = importlib.import_module(module_name)
            urlpatterns.append(
                path(f'{url_prefix}/', include(module_name))
            )
        except Exception as e:
            print(f"Error importing {module_name}: {e}")
