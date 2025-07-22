import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dualdb_memory.manager import DualDBManager
from dualdb_memory.summarizer_stub import StubSummarizer

# 写入轮次与线程数
THREAD_COUNT = 5
ROUNDS_PER_THREAD = 100

def worker(thread_id, mgr):
    """每个线程追加一批记录"""
    success = 0
    for i in range(ROUNDS_PER_THREAD):
        try:
            mgr.append("user", f"[T{thread_id}] user {i}")
            mgr.append("assistant", f"[T{thread_id}] assistant {i}")
            success += 1
        except Exception as e:
            print(f"Thread {thread_id} error at round {i}: {e}")
    return success

def run_stress_test():
    print(f"Starting stress test with {THREAD_COUNT} threads...")

    # 初始化输出目录
    out_dir = "demo_stress_output"
    os.makedirs(out_dir, exist_ok=True)

    # 创建共享 DualDBManager（JSON 后端）
    mgr = DualDBManager(
        storage_type="json",
        active_path=os.path.join(out_dir, "active.json"),
        archive_path=os.path.join(out_dir, "archive.json"),
        summarizer=StubSummarizer(),
        threshold=10,
    )

    # 使用线程池并发写入
    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        futures = [executor.submit(worker, i, mgr) for i in range(THREAD_COUNT)]
        results = [f.result() for f in as_completed(futures)]

    total_success = sum(results)
    print(f"\n✅ 写入完成：{total_success * 2} 条记录（{THREAD_COUNT} 线程 × {ROUNDS_PER_THREAD} 轮 × 2条/轮）")

if __name__ == "__main__":
    run_stress_test()
