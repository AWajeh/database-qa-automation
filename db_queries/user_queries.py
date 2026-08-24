"""Raw SQL queries used by tests to verify database state directly — completely bypassing
the application's own ORM layer, so a bug in the app's read path can't hide a bug in its
write path.
"""

import sqlite3


def get_connection(db_path="qa_app.db"):
    return sqlite3.connect(db_path)


def get_user_by_id(conn, user_id):
    cursor = conn.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


def get_user_by_username(conn, username):
    cursor = conn.execute(
        "SELECT id, username, email FROM users WHERE username = ?", (username,)
    )
    return cursor.fetchone()


def count_users(conn):
    cursor = conn.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]


def insert_user_raw(conn, user_id, username, email):
    """Inserts a row directly via SQL — used to test the database's own primary key
    constraint, independent of any validation the API layer might add on top."""
    conn.execute(
        "INSERT INTO users (id, username, email) VALUES (?, ?, ?)",
        (user_id, username, email),
    )
    conn.commit()


def delete_all_users(conn):
    conn.execute("DELETE FROM users")
    conn.commit()
