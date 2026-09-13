import json
from datetime import datetime

from app.config import DATA_DIR

NOTES_PATH = DATA_DIR / "task_notes.json"


def save_task_note(task_id: str, content: str) -> str:
    """保存任务结论到本地笔记文件。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    notes = {}
    if NOTES_PATH.exists():
        notes = json.loads(NOTES_PATH.read_text(encoding="utf-8"))
    notes[task_id] = {
        "content": content,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
    }
    NOTES_PATH.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"已保存到 task_notes.json，键名: {task_id}"
