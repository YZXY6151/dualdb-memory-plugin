# examples/demo_concurrent.py

import os
import csv
import time
import threading
from concurrent.futures import ThreadPoolExecutor

from dualdb_memory.store_sqlite import SQLiteStore
from dualdb_memory.memory import DualDBMemory
from dualdb_memory.summarizer_stub import StubSummarizer

# 输出目录
OUT_DIR = "demo_concurrent_output"
os.makedirs(OUT_DIR, exist_ok=True)

# 数据库文件
active_path  = os.path.join(OUT_DIR, "active.db")
archive_path = os.path.join(OUT_DIR, "archive.db")
log_path     = os.path.join(OUT_DIR, "latencies.csv")

# 1) 用异步 + WAL 模式的 SQLiteStore 创建存储
active_store  = SQLiteStore(active_path,  use_async=True)
archive_store = SQLiteStore(archive_path, use_async=True)

# 2) 直接用 DualDBMemory 组合
manager = DualDBMemory(
    active_store=active_store,
    archive_store=archive_store,
    summarizer=StubSummarizer(),
    threshold=10000,  # 足够大以避免轮回摘要打断测试
)

lock = threading.Lock()
log_rows = []

def write_pair(i: int):
    """一次 user+assistant 写入，记录耗时"""
    start = time.time()
    manager.append("user",      f"[T{i}] Hello from user")
    manager.append("assistant", f"[T{i}] Response from assistant")
    elapsed_ms = (time.time() - start) * 1000
    with lock:
        log_rows.append((i, elapsed_ms))

def run_concurrent_demo(workers: int = 8, rounds_per_thread: int = 500):
    total = workers * rounds_per_thread
    print(f"🔥 开始并发写入：{workers} 线程 × {rounds_per_thread} 轮 = {total} 次写入")
    with ThreadPoolExecutor(max_workers=workers) as execu:
        for i in range(total):
            execu.submit(write_pair, i)
    print("✅ 并发写入结束，正在写日志…")

    # 确保后台队列都 flush 完毕并关闭连接
    manager.close()

    # 保存 CSV
    with open(log_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["entry_id", "append_time_ms"])
        writer.writerows(log_rows)

    print(f"写入延迟日志保存在: {log_path}")

if __name__ == "__main__":
    run_concurrent_demo(workers=16, rounds_per_thread=2000)
