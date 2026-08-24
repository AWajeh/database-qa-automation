"""Fixtures: starts the real API server for real HTTP testing, provides a raw DB
connection for direct verification, and cleans up the database between tests.
"""

import os
import socket
import threading
import time

import pytest
import requests
import uvicorn

from app.main import app
from app.database import engine
from db_queries.user_queries import get_connection, delete_all_users

DB_PATH = "qa_app.db"
HOST = "127.0.0.1"


def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def api_url():
    """Runs the real FastAPI app in a background thread for the whole test session,
    so tests hit it over real HTTP with `requests` instead of an in-process test client.
    """
    port = _find_free_port()
    config = uvicorn.Config(app, host=HOST, port=port, log_level="warning")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    base_url = f"http://{HOST}:{port}"
    for _ in range(50):
        try:
            if requests.get(f"{base_url}/health", timeout=0.5).status_code == 200:
                break
        except requests.ConnectionError:
            time.sleep(0.1)
    else:
        raise RuntimeError("API server did not start in time")

    yield base_url

    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture
def db_conn():
    """A raw sqlite3 connection for querying the database directly, independent of the app."""
    conn = get_connection(DB_PATH)
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def clean_database(api_url):
    """Data cleanup fixture: guarantees every test starts with an empty `users` table."""
    conn = get_connection(DB_PATH)
    delete_all_users(conn)
    conn.close()
    yield


@pytest.fixture(scope="session", autouse=True)
def remove_db_file_after_session():
    yield
    engine.dispose()
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
