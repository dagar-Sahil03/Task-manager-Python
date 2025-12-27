"""
WSGI entry point for Gunicorn server.
"""

from app import app

if __name__ == "__main__":
    app.run()

