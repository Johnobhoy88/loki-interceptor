import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.server import app as flask_app  # noqa: E402


# Expose WSGI callable for Vercel's Python runtime
app = flask_app
