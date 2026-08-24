"""Full CRUD lifecycle, with the DELETE step verified directly against the database —
not just trusted from the API's status code.
"""

import requests

from db_queries.user_queries import get_user_by_id, count_users


def test_full_crud_lifecycle(api_url, db_conn):
    create_resp = requests.post(
        f"{api_url}/users", json={"username": "crud_user", "email": "crud@example.com"}
    )
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    read_resp = requests.get(f"{api_url}/users/{user_id}")
    assert read_resp.status_code == 200
    assert read_resp.json()["username"] == "crud_user"

    update_resp = requests.put(
        f"{api_url}/users/{user_id}", json={"email": "updated@example.com"}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["email"] == "updated@example.com"

    delete_resp = requests.delete(f"{api_url}/users/{user_id}")
    assert delete_resp.status_code == 204

    # Confirm deletion via the API...
    get_after_delete = requests.get(f"{api_url}/users/{user_id}")
    assert get_after_delete.status_code == 404

    # ...and independently, directly against the database.
    row = get_user_by_id(db_conn, user_id)
    assert row is None


def test_delete_removes_only_the_targeted_row(api_url, db_conn):
    first = requests.post(
        f"{api_url}/users", json={"username": "user_a", "email": "a@example.com"}
    ).json()
    requests.post(f"{api_url}/users", json={"username": "user_b", "email": "b@example.com"})

    requests.delete(f"{api_url}/users/{first['id']}")

    assert count_users(db_conn) == 1
