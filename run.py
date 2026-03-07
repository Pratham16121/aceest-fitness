"""
Run the Flask app without the debugger's host check (avoids 403 when opening
http://localhost:5000). Use this if you see "Access to localhost was denied"
or HTTP 403.

  python run.py

Then open: http://127.0.0.1:5000  or  http://localhost:5000
"""
import os

# Avoid Werkzeug debugger's strict trusted_hosts (localhost can trigger 403).
os.environ.setdefault("FLASK_DEBUG", "0")

from werkzeug.serving import run_simple

from app import app

if __name__ == "__main__":
    run_simple(
        "127.0.0.1",
        5000,
        app,
        use_debugger=False,
        use_reloader=True,
        reloader_interval=1,
    )
