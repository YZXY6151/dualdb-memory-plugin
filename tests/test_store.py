import time
import pytest
from dualdb_memory.store_json import JsonStore
from dualdb_memory.store_sqlite import SQLiteStore

def test_json_store(tmp_path):
    fp = tmp_path / "j.json"
    store = JsonStore(str(fp))
    assert store.get_entries() == []
    store.add_entry("u","hi", tags=["t"])
    assert store.get_entries()[0]["tags"] == ["t"]
    store.clear()
    assert store.get_entries() == []

def test_sqlite_store(tmp_path):
    dbf = tmp_path / "s.db"
    store = SQLiteStore(f"sqlite:///{dbf}")
    assert store.get_entries() == []
    store.add_entry("bot","ok", tags=["info"])
    time.sleep(0.1)  # 给异步写入留点时间
    rows = store.get_entries()
    assert rows and rows[0]["role"]=="bot" and rows[0]["tags"]==["info"]
    store.clear()
    assert store.get_entries() == []
