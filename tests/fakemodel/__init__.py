"""Invented Ollama stand-in for tests, with no external model dependency."""

from .core import FakeModel, FakeTransport

__all__ = ["FakeModel", "FakeTransport"]
