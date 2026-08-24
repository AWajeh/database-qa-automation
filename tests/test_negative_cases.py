"""Negative testing: the API and the database itself should both reject invalid or
duplicate data with the right error, rather than silently accepting it.
"""

import sqlite3

import pytest
import requests

from db_queries.user_queries import insert_user_raw


def test_duplicate_username_via_api_is_rejected(api_url):
    payload = {"username": "duplicate_user", "email": "dup1@example.com"}
    first = requests.post(f"{api_url}/users", json=payload)
    assert first.status_code == 201

    second = requests.post(f"{api_url}/users", json={**payload, "email": "dup2@example.com"})
    assert second.status_code == 409


def test_duplicate_primary_key_is_rejected_at_db_level(db_conn):
    insert_user_raw(db_conn, 1, "raw_user_1", "raw1@example.com")

    with pytest.raises(sqlite3.IntegrityError):
        insert_user_raw(db_conn, 1, "raw_user_2", "raw2@example.com")


def test_invalid_email_format_is_rejected(api_url):
    response = requests.post(
        f"{api_url}/users", json={"username": "bad_email_user", "email": "not-an-email"}
    )
    assert response.status_code == 422


def test_username_too_short_is_rejected(api_url):
    response = requests.post(
        f"{api_url}/users", json={"username": "ab", "email": "short@example.com"}
    )
    assert response.status_code == 422


def test_missing_required_field_is_rejected(api_url):
    response = requests.post(f"{api_url}/users", json={"username": "no_email_user"})
    assert response.status_code == 422
