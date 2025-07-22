import time
import pytest
from dualdb_memory.memory import DualDBMemory
from dualdb_memory.store_json import JsonStore
from dualdb_memory.summarizer_stub import StubSummarizer

@pytest.fixture
def stores(tmp_path):
    a = JsonStore(str(tmp_path/"a.json"))
    b = JsonStore(str(tmp_path/"b.json"))
    return a, b

def test_threshold_trigger(stores):
    active, archive = stores
    mem = DualDBMemory(active,archive,StubSummarizer(), threshold=2, keywords=[], time_delta=None)
    mem.append("u","x")
    assert len(active.get_entries())==1 and not archive.get_entries()
    mem.append("u","y")
    assert not active.get_entries() and len(archive.get_entries())==1

def test_time_trigger(stores):
    active, archive = stores
    mem = DualDBMemory(active,archive,StubSummarizer(), threshold=100, keywords=[], time_delta=0.05)
    mem.append("u","t1")
    time.sleep(0.06)
    mem.append("u","t2")
    assert len(archive.get_entries())==1

def test_force_rotate_on_empty(stores):
    active, archive = stores
    mem = DualDBMemory(active,archive,StubSummarizer(), threshold=100)
    # 直接调用 _check_and_rotate()，即使没有消息也不报错
    mem._check_and_rotate()
    assert not active.get_entries() and not archive.get_entries()
