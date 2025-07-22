import csv
import json
import os
import time
import matplotlib.pyplot as plt

from dualdb_memory.manager import DualDBManager
from dualdb_memory.summarizer_stub import StubSummarizer

def load_json_list(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []

def run_perf_test(rounds=100000, threshold=1000):
    out_dir = "demo_perf_output"
    os.makedirs(out_dir, exist_ok=True)

    active_path = os.path.join(out_dir, "active_perf.json")
    archive_path = os.path.join(out_dir, "archive_perf.json")

    mgr = DualDBManager(
        storage_type="json",
        active_path=active_path,
        archive_path=archive_path,
        summarizer=StubSummarizer(),
        threshold=threshold,
    )

    metrics = []

    for i in range(1, rounds + 1):
        start = time.time()

        mgr.append("user", f"User message {i}")
        mgr.append("assistant", f"Assistant reply {i}")

        elapsed_ms = (time.time() - start) * 1000

        active_entries = load_json_list(active_path)
        archive_entries = load_json_list(archive_path)
        metrics.append((i, len(active_entries), len(archive_entries), round(elapsed_ms, 4)))

    # 写入 CSV
    csv_path = os.path.join(out_dir, "metrics.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["round", "active_count", "archive_count", "append_time_ms"])
        writer.writerows(metrics)

    # 绘制写入时间图
    rounds_list, active_counts, archive_counts, times = zip(*metrics)
    plt.figure(figsize=(10, 4))
    plt.plot(rounds_list, times, label="append_time_ms", linewidth=0.6)
    plt.xlabel("Round")
    plt.ylabel("Append Time (ms)")
    plt.title("Write Time per Round (10000 rounds)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "times.png"))

    # 绘制 active/archive 增长图
    plt.figure(figsize=(10, 4))
    plt.plot(rounds_list, active_counts, label="active_count")
    plt.plot(rounds_list, archive_counts, label="archive_count")
    plt.xlabel("Round")
    plt.ylabel("Entry Count")
    plt.title("Memory Growth Over Time")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "counts.png"))

    print(f"✅ 测试完成！结果保存至 {out_dir}/metrics.csv、times.png、counts.png")

if __name__ == "__main__":
    run_perf_test()
