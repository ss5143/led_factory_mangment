#!/usr/bin/env python
import os
import sys
import time
import threading
import webbrowser

# Handlers for --noconsole mode when stdout/stderr don't exist
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'led_factory.settings')

def open_browser():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8001/")

def main():
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Django import nahi ho saka.") from exc

    if len(sys.argv) == 1:
        threading.Thread(target=open_browser, daemon=True).start()
        sys.argv = ['manage.py', 'runserver', '127.0.0.1:8001', '--noreload']

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()