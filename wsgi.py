"""WSGI entrypoint for production servers (gunicorn)."""
from app import server

# Export the WSGI application callable as 'app' and 'server' for compatibility
app = server
