import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from datetime import datetime

from config import DATABASE_URL


@contextmanager
def get_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
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
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                joined_at TEXT
            )
        """)


def add_movie(code, title, year, genre, duration, language, quality, file_id):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO movies
               (code, title, year, genre, duration, language, quality, file_id, views, added_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, %s)""",
            (code, title, year, genre, duration, language, quality, file_id, datetime.now().isoformat()),
        )


def code_exists(code) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM movies WHERE code = %s", (code,))
        return cur.fetchone() is not None


def get_movie(code):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM movies WHERE code = %s", (code,))
        row = cur.fetchone()
        return dict(row) if row else None


def increment_views(code):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE movies SET views = views + 1 WHERE code = %s", (code,))


def delete_movie(code) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM movies WHERE code = %s", (code,))
        return cur.rowcount > 0


def update_movie_field(code, field, value) -> bool:
    allowed_fields = {"title", "year", "genre", "duration", "language", "quality", "file_id"}
    if field not in allowed_fields:
        return False
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"UPDATE movies SET {field} = %s WHERE code = %s", (value, code))
        return cur.rowcount > 0


def list_movies(genre=None, limit=10, offset=0):
    with get_connection() as conn:
        cur = conn.cursor()
        if genre:
            cur.execute(
                "SELECT code, title FROM movies WHERE genre = %s ORDER BY code LIMIT %s OFFSET %s",
                (genre, limit, offset),
            )
        else:
            cur.execute(
                "SELECT code, title FROM movies ORDER BY code LIMIT %s OFFSET %s",
                (limit, offset),
            )
        return [dict(r) for r in cur.fetchall()]


def count_movies(genre=None):
    with get_connection() as conn:
        cur = conn.cursor()
        if genre:
            cur.execute("SELECT COUNT(*) AS c FROM movies WHERE genre = %s", (genre,))
        else:
            cur.execute("SELECT COUNT(*) AS c FROM movies")
        return cur.fetchone()["c"]


def get_genres():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT DISTINCT genre FROM movies WHERE genre IS NOT NULL AND genre != '' ORDER BY genre"
        )
        return [r["genre"] for r in cur.fetchall()]


def top_movies(limit=10):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT code, title, views FROM movies ORDER BY views DESC LIMIT %s", (limit,)
        )
        return [dict(r) for r in cur.fetchall()]


def add_user(user_id, username):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO users (user_id, username, joined_at) VALUES (%s, %s, %s)
               ON CONFLICT (user_id) DO NOTHING""",
            (user_id, username, datetime.now().isoformat()),
        )


def count_users():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS c FROM users")
        return cur.fetchone()["c"]
def get_all_user_ids():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users")
        return [r["user_id"] for r in cur.fetchall()]