"""Main entry point for the Chora ASGI server application.

When started with 'python -m chora'.
"""

from chora.asgi_server import run

__all__ = ["run"]

if __name__ == "__main__":
    run()
