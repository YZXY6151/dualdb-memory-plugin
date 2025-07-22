import pytest
import tempfile
import os
from dualdb_memory.manager import DualDBManager
from dualdb_memory.summarizer_stub import StubSummarizer

@pytest.fixture
def tmp_paths(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    return str(d / "active.json"), str(d / "archive.json")

@pytest.fixture
def manager(tmp_paths):
    active, archive = tmp_paths
    mgr = DualDBManager(
        storage_type="json",
        active_path=active,
        archive_path=archive,
        summarizer=StubSummarizer(),
        threshold=3,       # 小阈值，便于测试
        keywords=[],       # 关闭关键词触发
        time_delta=None    # 关闭定时触发
    )
    yield mgr
    mgr.close()
