import json
import sqlite3
from datetime import datetime

from app.config import DATA_DIR, DB_PATH


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS task_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                status TEXT NOT NULL,
                total_ms INTEGER,
                trace_json TEXT NOT NULL,
                final_answer TEXT,
                created_at TEXT NOT NULL
            )
            """
        )


def save_task_run(
    task: str,
    *,
    status: str,
    total_ms: int,
    trace: list[dict],
    final_answer: str,
) -> int:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            """
            INSERT INTO task_runs (task, status, total_ms, trace_json, final_answer, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                task,
                status,
                total_ms,
                json.dumps(trace, ensure_ascii=False),
                final_answer,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        return int(cur.lastrowid)
