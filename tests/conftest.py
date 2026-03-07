"""Pytest fixtures for ACEest Fitness Flask application."""
import pytest

from app import app as flask_app


@pytest.fixture
def app():
    """Flask application instance with testing config."""
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(app):
    """Flask test client for making requests."""
    return app.test_client()
