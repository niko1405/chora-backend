"""Main entry point for the Chora ASGI server application."""

from chora.asgi_server import run

__all__ = ["run"]

if __name__ == "__main__":
    run()
