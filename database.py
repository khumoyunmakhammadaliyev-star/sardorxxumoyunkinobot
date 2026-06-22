import sqlite3
from contextlib import contextmanager
from datetime import datetime

from config import DB_PATH


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                code INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                year TEXT,
                genre TEXT,
                duration TEXT,
                language TEXT,
                quality TEXT,
                file_id TEXT NOT NULL,
                views INTEGER DEFAULT 0,
                added_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                joined_at TEXT
            )
        """)


def add_movie(code, title, year, genre, duration, language, quality, file_id):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO movies
               (code, title, year, genre, duration, language, quality, file_id, views, added_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)""",
            (code, title, year, genre, duration, language, quality, file_id, datetime.now().isoformat()),
        )


def code_exists(code) -> bool:
    with get_connection() as conn:
        row = conn.execute("SELECT 1 FROM movies WHERE code = ?", (code,)).fetchone()
        return row is not None


def get_movie(code):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM movies WHERE code = ?", (code,)).fetchone()
        return dict(row) if row else None


def increment_views(code):
    with get_connection() as conn:
        conn.execute("UPDATE movies SET views = views + 1 WHERE code = ?", (code,))


def delete_movie(code) -> bool:
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM movies WHERE code = ?", (code,))
        return cur.rowcount > 0


def update_movie_field(code, field, value) -> bool:
    allowed_fields = {"title", "year", "genre", "duration", "language", "quality", "file_id"}
    if field not in allowed_fields:
        return False
    with get_connection() as conn:
        cur = conn.execute(f"UPDATE movies SET {field} = ? WHERE code = ?", (value, code))
        return cur.rowcount > 0


def list_movies(genre=None, limit=10, offset=0):
    with get_connection() as conn:
        if genre:
            rows = conn.execute(
                "SELECT code, title FROM movies WHERE genre = ? ORDER BY code LIMIT ? OFFSET ?",
                (genre, limit, offset),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT code, title FROM movies ORDER BY code LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        return [dict(r) for r in rows]


def count_movies(genre=None):
    with get_connection() as conn:
        if genre:
            row = conn.execute("SELECT COUNT(*) AS c FROM movies WHERE genre = ?", (genre,)).fetchone()
        else:
            row = conn.execute("SELECT COUNT(*) AS c FROM movies").fetchone()
        return row["c"]


def get_genres():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT genre FROM movies WHERE genre IS NOT NULL AND genre != '' ORDER BY genre"
        ).fetchall()
        return [r["genre"] for r in rows]


def top_movies(limit=10):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT code, title, views FROM movies ORDER BY views DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def add_user(user_id, username):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username, joined_at) VALUES (?, ?, ?)",
            (user_id, username, datetime.now().isoformat()),
        )


def count_users():
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()
        return row["c"]