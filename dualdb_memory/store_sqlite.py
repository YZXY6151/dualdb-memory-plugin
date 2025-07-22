import os
import sqlite3
import threading
import queue
import json
import time
from typing import Any, Dict, List, Optional

class SQLiteStore:
    def __init__(
        self,
        db_path: str,
        use_async: bool = True,
        checkpoint_interval: int = 10  # 每 N 秒做一次 checkpoint
    ):
        self.db_path = db_path.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self.use_async = use_async
        self.lock = threading.Lock()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.conn.execute("PRAGMA busy_timeout=5000;")
        # 每写入 20 页（≈80 KB）自动 checkpoint，避免 WAL 文件膨胀
        self.conn.execute("PRAGMA wal_autocheckpoint=20;")
        # 将 WAL/journal 文件大小限制在 512 KB
        self.conn.execute("PRAGMA journal_size_limit=524288;")

        self._init_db()

        if self.use_async:
            self.queue = queue.Queue()
            self.stop_event = threading.Event()

            # 写入线程
            self.worker_thread = threading.Thread(target=self._write_worker, daemon=True)
            self.worker_thread.start()

            # 定时 checkpoint 线程
            self.checkpoint_thread = threading.Thread(target=self._periodic_checkpoint, daemon=True)
            self.checkpoint_thread.start()

        else:
            self.stop_event = None

    def _init_db(self):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT
                )
            """)
            self.conn.commit()

    def _write_worker(self):
        while not self.stop_event.is_set():
            try:
                role, content, tags = self.queue.get(timeout=0.1)
                self._write_to_db(role, content, tags)
                self.queue.task_done()
            except queue.Empty:
                continue

    def _periodic_checkpoint(self):
        while not self.stop_event.is_set():
            time.sleep(10)
            with self.lock:
                # 使用 RESTART 模式，彻底重置 WAL 日志
                self.conn.execute("PRAGMA wal_checkpoint(RESTART);")
            # 删除已合并的 WAL 和 SHM 文件，避免其持续膨胀
            try:
                wal_path = self.db_path + "-wal"
                shm_path = self.db_path + "-shm"
                if os.path.exists(wal_path):
                    os.remove(wal_path)
                if os.path.exists(shm_path):
                    os.remove(shm_path)
            except Exception:
                # 忽略删除过程中的任何错误
                pass

    def _write_to_db(self, role: str, content: str, tags: Optional[List[str]] = None):
        tags_json = json.dumps(tags, ensure_ascii=False) if tags else None
        with self.lock:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO entries(role, content, tags) VALUES (?, ?, ?)",
                (role, content, tags_json)
            )
            self.conn.commit()

    def add_entry(self, role: str, content: str, tags: Optional[List[str]] = None) -> None:
        if self.use_async:
            self.queue.put((role, content, tags))
        else:
            self._write_to_db(role, content, tags)

    def get_entries(self) -> List[Dict[str, Any]]:
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT role, content, tags FROM entries ORDER BY id")
            rows = cur.fetchall()

        result = []
        for role, content, tags_json in rows:
            entry: Dict[str, Any] = {"role": role, "content": content}
            if tags_json:
                entry["tags"] = json.loads(tags_json)
            result.append(entry)
        return result

    def clear(self) -> None:
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM entries")
            self.conn.commit()

    def close(self):
        if self.use_async:
            self.queue.join()
            self.stop_event.set()
            self.worker_thread.join()
            self.checkpoint_thread.join()
        self.conn.close()
