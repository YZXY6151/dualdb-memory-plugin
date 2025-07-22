# Usage & Test Guide for DualDB Memory Plugin

This document provides detailed usage examples, system architecture, rotation logic, and test results for the [dualdb-memory-plugin](../README.md).

---

## 📚 Table of Contents

- [1. Usage Examples](#1-usage-examples)
  - [1.1 JSON Storage](#11-json-storage)
  - [1.2 SQLite Storage](#12-sqlite-storage)
  - [1.3 Replace the Summarizer](#13-replace-the-summarizer)
- [2. Architecture & Logic](#2-architecture--logic)
  - [2.1 Internal Structure](#21-internal-structure)
  - [2.2 Rotation Triggers](#22-rotation-triggers)
- [3. Testing & Evaluation](#3-testing--evaluation)
  - [3.1 Stability Test](#31-stability-test)
  - [3.2 Concurrency Test](#32-concurrency-test)
  - [3.3 Performance Profiling](#33-performance-profiling)
  - [3.4 Stress Test](#34-stress-test)
  - [3.5 Trigger Combination Test](#35-trigger-combination-test)
- [4. Output Formats](#4-output-formats)
- [5. Performance Notes](#5-performance-notes)




---

## 1. Usage Examples

This plugin supports both file-based (JSON) and concurrent (SQLite) backends, and allows custom summarization engines to be injected.

### 1.1 JSON Storage (Simple Example)

```python
from dualdb_memory.manager import DualDBManager
from dualdb_memory.summarizer_stub import StubSummarizer

manager = DualDBManager(
    storage_type="json",
    active_path="data/active.json",
    archive_path="data/archive.json",
    summarizer=StubSummarizer(),
    threshold=3,
    keywords=["important", "urgent"],
    time_delta=60  # Rotate if 60s passed
)

manager.append("user", "What's the weather today?")
manager.append("assistant", "Sunny and 25°C.")
context = manager.get_context()
print(context)  # Shows active + archive entries
```

---

### 1.2 SQLite Storage (Recommended for Concurrency)

```python
from dualdb_memory.manager import DualDBManager
from dualdb_memory.summarizer_stub import StubSummarizer

manager = DualDBManager(
    storage_type="sqlite",
    active_path="data/active.db",
    archive_path="data/archive.db",
    summarizer=StubSummarizer(),
    threshold=5
)

manager.append("user", "Hi again")
manager.append("assistant", "Hello!")
```

SQLite backend supports **WAL mode** and **async queue**, enabling safe high-frequency writes.

---

### 1.3 Replace the Summarizer

To use your own summarizer (e.g., OpenAI API, T5, or local LLM):

1. Extend the `BaseSummarizer` class  
2. Implement the `summarize()` method

```python
from dualdb_memory.summarizer_base import BaseSummarizer

class MySummarizer(BaseSummarizer):
    def summarize(self, texts):
        return "Summary: " + texts[0], ["auto"]
```

Then pass it into `DualDBManager(summarizer=MySummarizer())`.



---

## 2. Architecture & Logic

This section explains the internal structure and rotation mechanics of the DualDB memory plugin.

### 2.1 Internal Structure

```
DualDBMemory
├── active_store     # Short-term memory (JSON or SQLite)
├── archive_store    # Long-term memory (JSON or SQLite)
├── summarizer       # Pluggable summarization engine
└── triggers         # Rotation triggers (threshold | keyword | time)
```

The entire logic is unified through `DualDBManager`, which handles appending messages, rotating to archive, and retrieving the current memory context.

### 2.2 Key Modules

| Module                    | Description                                      |
|---------------------------|--------------------------------------------------|
| `manager.py`              | Unified public interface (`append`, `get_context`) |
| `memory.py`               | Core memory control logic                        |
| `store_json.py`           | File-based storage for memory entries            |
| `store_sqlite.py`         | SQLite backend with WAL + async support          |
| `summarizer_base.py`      | Abstract summarizer interface                    |
| `summarizer_stub.py`      | Default dummy summarizer                         |
| `summarizer_openai.py`    | Optional OpenAI summarizer                       |

---

### 2.3 Rotation Triggers

Memory rotates from active → archive when **any one** of the following is satisfied:

- `threshold`: Max number of messages in active memory
- `keywords`: Trigger keywords appear in a message
- `time_delta`: Time elapsed since last archive operation

All triggers are optional and can be combined.  
After rotation, active memory is cleared and a summary is stored in archive memory with tags.

```python
DualDBManager(..., threshold=5, keywords=["urgent"], time_delta=30)
```

You can track rotation activity by inspecting logs or printing `manager.get_context()`.



---

## 3. Testing & Evaluation

The plugin has been tested across five dimensions to ensure reliability, concurrency, and trigger correctness.

---

### 3.1 Stability Test

- **Goal:** Validate long-term execution without crash or memory leaks
- **Script:** `examples/demo_stability.py`
- **Duration:** 1 hour continuous run
- **Backend:** JSON
- **Output:** `log.csv`, `active.json`, `archive.json`
- **Result:** No errors. Memory behaved consistently across cycles.

---

### 3.2 Concurrency Test

- **Goal:** Evaluate robustness under multi-threaded writes
- **Script:** `examples/demo_concurrent.py`
- **Threads:** 5
- **Rounds:** 10,000+ total
- **Backend:** SQLite with WAL mode + async queue
- **Output:** `log.csv`, `active.db`, `archive.db`
- **Result:** No collisions; latency remained stable; excellent WAL performance.

---

### 3.3 Performance Profiling

- **Goal:** Measure write latency & memory growth
- **Script:** `examples/demo_perf.py`
- **Backend:** SQLite (WAL)
- **Output Files:**
  - `latencies.csv`: per-write latency
  - `metrics.csv`: size over time
  - `times.png`, `counts.png`: visualizations
- **Result:** Average append latency: **~5–10ms**; smooth memory growth with clear rotation points.

---

### 3.4 Stress Test

- **Goal:** Simulate rapid fire, burst-style writing
- **Script:** `examples/demo_stress.py`
- **Mode:** No delay, rapid appends
- **Rounds:** 10,000+
- **Backend:** SQLite (WAL)
- **Output:** `log.csv`
- **Result:** Some jitter under burst, but no crash or slowdown observed.

---

### 3.5 Trigger Combination Test

- **Goal:** Ensure threshold + keyword + time triggers work independently or together
- **Script:** `examples/demo_full.py`
- **Settings:**
  - `threshold = 5`
  - `keywords = ['important']`
  - `time_delta = 5`
- **Result:** Each trigger caused successful memory rotation; tag generation confirmed.

---

💡 All tests produce logs and summary files, and are fully reproducible by running the corresponding Python scripts.

```bash
python examples/demo_stability.py
python examples/demo_concurrent.py
...
```


---

## 4. Output Formats

All memory entries—whether in `active` or `archive`—follow the same schema:

```json
{
  "role": "user" | "assistant" | "system",
  "content": "Text content here",
  "tags": ["optional", "labels", "summary"]
}
```

- `active` memory: Raw, recent user-assistant messages
- `archive` memory: Summarized or compressed entries with optional tags

Outputs are saved as:

- `.json` (for `JsonStore`)
- `.db` (SQLite + optional `.csv` logs)
- Optional plots and logs depending on test

---

## 5. Performance Notes

- SQLite backend uses **WAL mode + async write queue** for concurrency
- Handles **10k+ writes** with minimal latency impact
- Safe for **multi-threaded access** under normal loads
- Summarizer stub ensures testability without external dependencies

✅ No GPU or API keys required  
✅ Ideal for resource-constrained or experimental environments  
✅ Use logs (`log.csv`) to analyze write patterns and rotation behavior

---

```bash
# Example: Full trigger test
python examples/demo_full.py
```

You are encouraged to explore the examples and compare performance under different backends.

---
