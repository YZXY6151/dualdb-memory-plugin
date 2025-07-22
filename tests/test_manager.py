import pytest
from dualdb_memory.manager import DualDBManager
from dualdb_memory.summarizer_stub import StubSummarizer

@pytest.fixture
def mgr(tmp_path):
    # 在 tmp_path 下生成两个文件路径
    active = str(tmp_path / "active.json")
    archive = str(tmp_path / "archive.json")

    # 阈值设为 3，用于测试 append 触发和 force_rotate
    m = DualDBManager(
        storage_type="json",
        active_path=active,
        archive_path=archive,
        summarizer=StubSummarizer(),
        threshold=3,
        keywords=[],      # 关闭关键词触发
        time_delta=None   # 关闭定时触发
    )
    yield m
    # 释放底层资源
    m.close()

def test_append_and_context(mgr):
    # 依次 append 3 条，达到 threshold 后会自动归档一次
    mgr.append("user", "msg1")
    mgr.append("assistant", "msg2")
    mgr.append("user", "msg3")

    ctx = mgr.get_context()
    # 此时只剩下归档的那一条摘要
    assert isinstance(ctx, list)
    assert len(ctx) == 1
    assert ctx[0]["role"] == "system"
    assert "摘要" in ctx[0]["content"]

def test_clear_all(mgr):
    # append 一条，再 clear_all，get_context 应返回空
    mgr.append("user", "hello")
    mgr.clear_all()
    assert mgr.get_context() == []

def test_force_rotate(mgr):
    # append 2 条，还没到 threshold (3)，get_context 应有两条原始消息
    mgr.append("user", "a")
    mgr.append("user", "b")
    ctx_before = mgr.get_context()
    assert len(ctx_before) == 2
    assert all(entry["role"] in ("user", "assistant") for entry in ctx_before)

    # 强制触发归档
    mgr.force_rotate()
    ctx_after = mgr.get_context()
    # 归档后，只剩下一条 system 摘要
    assert len(ctx_after) == 1
    assert ctx_after[0]["role"] == "system"
    assert "摘要" in ctx_after[0]["content"]
