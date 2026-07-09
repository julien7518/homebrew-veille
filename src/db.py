import os
import sqlite3
from datetime import datetime

DB_PATH = os.environ.get("DB_PATH", "DB/veille.db")


def get_conn():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS seen_packages (
            name TEXT PRIMARY KEY,
            kind TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at TEXT NOT NULL,
            status TEXT NOT NULL,
            packages_count INTEGER DEFAULT 0,
            error_message TEXT
        );
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()


def get_config(key: str) -> str | None:
    conn = get_conn()
    row = conn.execute("SELECT value FROM config WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else None


def set_config(key: str, value: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO config (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?",
        (key, value, value),
    )
    conn.commit()
    conn.close()


def is_seen(name: str) -> bool:
    conn = get_conn()
    row = conn.execute("SELECT 1 FROM seen_packages WHERE name = ?", (name,)).fetchone()
    conn.close()
    return row is not None


def mark_seen(name: str, kind: str):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO seen_packages (name, kind) VALUES (?, ?)",
        (name, kind),
    )
    conn.commit()
    conn.close()


def log_email_run(
    status: str, packages_count: int = 0, error_message: str | None = None
):
    conn = get_conn()
    conn.execute(
        "INSERT INTO email_logs (run_at, status, packages_count, error_message) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), status, packages_count, error_message),
    )
    conn.commit()
    conn.close()


def get_last_log():
    conn = get_conn()
    row = conn.execute("SELECT * FROM email_logs ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return dict(row) if row else None


def get_logs(limit: int = 50):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM email_logs ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def count_seen() -> int:
    conn = get_conn()
    row = conn.execute("SELECT COUNT(*) AS c FROM seen_packages").fetchone()
    conn.close()
    return row["c"]
