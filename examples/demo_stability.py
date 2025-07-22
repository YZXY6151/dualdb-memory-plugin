# examples/demo_stability.py

import os
import time
import random
from datetime import datetime
from dualdb_memory.summarizer_stub import StubSummarizer

from dualdb_memory.manager import DualDBManager

# 1. 创建输出目录
output_dir = "demo_stability_output"
os.makedirs(output_dir, exist_ok=True)

# 2. 初始化 DualDB 管理器
active_path = os.path.join(output_dir, "active.json")
archive_path = os.path.join(output_dir, "archive.json")
log_file = os.path.join(output_dir, "log.csv")

db = DualDBManager(
    storage_type="json",
    active_path=active_path,
    archive_path=archive_path,
    summarizer=StubSummarizer(), 
    threshold=10
)


# 3. 写入 CSV 文件头
with open(log_file, "w", encoding="utf-8") as f:
    f.write("timestamp,append_time_ms\n")

print("✅ 稳定性测试启动，每2秒写入一次。按 Ctrl+C 停止。")

# 4. 循环测试
try:
    round = 0
    while True:
        round += 1
        user_msg = f"[{round}] user message {random.randint(1000,9999)}"
        ai_msg = f"[{round}] assistant reply {random.randint(1000,9999)}"

        start = time.time()
        db.append("user", user_msg)
        db.append("assistant", ai_msg)
        elapsed_ms = (time.time() - start) * 1000

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now_str}] Round {round} | Append time: {elapsed_ms:.2f} ms")

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{now_str},{elapsed_ms:.2f}\n")

        time.sleep(2)

except KeyboardInterrupt:
    print("\n🛑 测试终止，日志保存在 demo_stability_output/log.csv")
