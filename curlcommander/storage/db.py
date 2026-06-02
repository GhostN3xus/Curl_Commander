import sqlite3
from pathlib import Path

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS history (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        TEXT NOT NULL,
    method    TEXT NOT NULL,
    url       TEXT NOT NULL,
    headers   TEXT,
    params    TEXT,
    body      TEXT,
    body_type TEXT,
    auth_type TEXT,
    status    INTEGER,
    duration  REAL,
    curl_cmd  TEXT
);
"""


def open_connection(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    conn.commit()
