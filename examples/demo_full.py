# examples/demo_full.py

import csv
import json
import os
from time import sleep

import matplotlib.pyplot as plt

from dualdb_memory.manager import DualDBManager
from dualdb_memory.summarizer_stub import StubSummarizer

def load_json_list(path):
    """如果文件存在，返回解析后的列表；否则返回空列表"""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []

def run_demo(rounds=50, threshold=10):
    # 1) 确保输出目录存在
    out_dir = "demo_full_output"
    os.makedirs(out_dir, exist_ok=True)

    # 2) 初始化 DualDBManager，指定输出文件到 demo_full_output/
    active_path = os.path.join(out_dir, "active_demo.json")
    archive_path = os.path.join(out_dir, "archive_demo.json")
    mgr = DualDBManager(
        storage_type="json",
        active_path=active_path,
        archive_path=archive_path,
        summarizer=StubSummarizer(),
        threshold=threshold,
    )

    metrics = []  # 存储 (轮次, active_count, archive_count)

    # 3) 模拟对话并收集 Active/Archive 条目数
    for i in range(1, rounds + 1):
        mgr.append("user", f"User message {i}")
        mgr.append("assistant", f"Assistant reply {i}")

        # 直接从 JSON 文件读取最新条目
        active_entries = load_json_list(active_path)
        archive_entries = load_json_list(archive_path)
        metrics.append((i, len(active_entries), len(archive_entries)))

        sleep(0.01)  # 模拟实时性

    # 4) 写入 CSV
    csv_path = os.path.join(out_dir, "metrics.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["round", "active_count", "archive_count"])
        writer.writerows(metrics)

    # 5) 绘制并保存折线图
    rounds_list, active_counts, archive_counts = zip(*metrics)
    plt.figure(figsize=(8, 4))
    plt.plot(rounds_list, active_counts, label="Active count")
    plt.plot(rounds_list, archive_counts, label="Archive count")
    plt.xlabel("Round")
    plt.ylabel("Entry count")
    plt.title("DualDB Memory Growth over Rounds")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "metrics.png"))

    print(f"演示完成！结果保存在 {out_dir}/metrics.csv 和 metrics.png")

if __name__ == "__main__":
    run_demo()
