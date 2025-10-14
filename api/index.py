import os
import sys

from vercel_wsgi import handle_request

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.server import app  # noqa: E402


def handler(request, response):
    """Vercel entry point wrapping the Flask app."""
    return handle_request(app, request, response)
