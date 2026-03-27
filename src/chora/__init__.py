"""Chora package for ASGI server and FastAPI application."""

from chora.asgi_server import run
from chora.fastapi_app import app

__all__ = ["app", "main"]


def main():  # noqa: RUF067
    """main-Funktion, damit das Modul als Skript aufgerufen werden kann."""
    run()
