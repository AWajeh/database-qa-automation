"""Verifies that data written through the API is correctly persisted in the database —
queried independently of the API, not just trusted from its response body.
"""

import requests

from db_queries.user_queries import get_user_by_username


def test_created_user_is_persisted_correctly_in_db(api_url, db_conn):
    payload = {"username": "integrity_user", "email": "integrity@example.com"}
    response = requests.post(f"{api_url}/users", json=payload)
    assert response.status_code == 201

    row = get_user_by_username(db_conn, "integrity_user")
    assert row is not None
    assert row[1] == "integrity_user"
    assert row[2] == "integrity@example.com"


def test_updated_email_is_reflected_in_db(api_url, db_conn):
    create_resp = requests.post(
        f"{api_url}/users", json={"username": "update_user", "email": "old@example.com"}
    )
    user_id = create_resp.json()["id"]

    update_resp = requests.put(f"{api_url}/users/{user_id}", json={"email": "new@example.com"})
    assert update_resp.status_code == 200

    row = get_user_by_username(db_conn, "update_user")
    assert row[2] == "new@example.com"
