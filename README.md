# dualdb-memory-plugin

[![PyPI](https://img.shields.io/pypi/v/dualdb-memory-plugin.svg)](https://pypi.org/project/dualdb-memory-plugin/)
[![License](https://img.shields.io/badge/license-CC--BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Build Status](https://github.com/YZXY6151/dualdb-memory-plugin/actions/workflows/python-test.yml/badge.svg)](https://github.com/YZXY6151/dualdb-memory-plugin/actions)

---

**DualDB Memory Plugin** is a lightweight memory cycling system for AI dialogue agents, simulating human-like memory transitions from short-term to long-term.  
It supports both **JSON** and **SQLite** backends and features a **pluggable summarizer interface**.

---

## 📌 Originality & Archival Record

This project was originally developed and published by **YZXY6151** in July 2025.

🧾 **Design & Originality Declaration**  
📄 [Archive.org Snapshot (EN)](https://archive.org/details/dual-db-memory-plugin-originality-en)  
📅 Archived on: 2025-07-22

💻 **Source Code Snapshot (Software Heritage)**  
🔗 [Permanent snapshot](https://archive.softwareheritage.org/browse/snapshot/20c63a71da5a33884f1615b18fcec904f99de0bb/)  
🆔 `swh:1:snp:20c63a71da5a33884f1615b18fcec904f99de0bb`  
📅 Archived on: 2025-07-23

📜 License: **CC BY-NC-SA 4.0 International**  
> Attribution required. Non-commercial reuse and modification allowed under the license terms.

---

_We welcome contributions, integrations, and community feedback. If you adapt or build upon this work, please preserve authorship and link to the archival records above._
 the terms of attribution and non-commercial use.


---

## ✨ Features

- **Human-like Memory Simulation**  
  Short-term dialogue entries (`active`) are rotated to long-term archive (`archive`) based on:
  - **Threshold** (number of messages)
  - **Keyword triggers**
  - **Time intervals**

- **Pluggable Summarization**  
  Replaceable summarizer engine. Default is a stub; you can plug in OpenAI, T5, or any local model.

- **Dual Backend Support**  
  Choose from:
  - `JsonStore`: File-based storage
  - `SQLiteStore`: Async + WAL mode for high concurrency

- **Minimal Dependencies**  
  No external packages required unless using `openai`.

---

## 🚀 Quick Start

### 1. Install from source

```bash
git clone https://github.com/YZXY6151/dualdb-memory-plugin.git
cd dualdb-memory-plugin
pip install -e .


from dualdb_memory.manager import DualDBManager
from dualdb_memory.summarizer_stub import StubSummarizer

manager = DualDBManager(
    storage_type="json",
    active_path="data/active.json",
    archive_path="data/archive.json",
    summarizer=StubSummarizer(),
    threshold=5,
    keywords=["urgent", "important"],
    time_delta=30
)

manager.append("user", "Hello!")
manager.append("assistant", "How can I help?")
context = manager.get_context()
print(context)


## 🔍 When to Use

✅ **Recommended for:**

- Chatbots or agents needing **short-to-long memory evolution**
- Projects without **vector DBs or external APIs**
- **Lightweight**, transparent memory workflows
- Educational or experimental AI setups

🛑 **Not ideal if:**

- You need **semantic search** or vector-based retrieval
- You're using large frameworks (e.g., LangChain) with built-in memory
- You require **multi-user**, role-based memory (planned extension)

---

## ⚖️ Design Comparison

| Feature                  | LangChain / MemoryGPT            | **DualDB Memory Plugin**               |
|--------------------------|----------------------------------|----------------------------------------|
| Dependency               | Heavy (pydantic, chroma, openai) | **Minimal** (stdlib only)              |
| Storage Format           | Vector DB / internal             | **JSON / SQLite**                      |
| Rotation Mechanism       | Often manual                     | **Auto** (threshold / keyword / time)  |
| Summarizer Integration   | Hard to customize                | **Pluggable Interface**                |
| Modularity               | Tightly coupled                  | **Loosely coupled**                    |
| Learning Curve           | Medium–High                      | **Low**, quick integration             |

---


## 📘 Full Documentation

Looking for full usage examples, architecture, and test results?

👉 **[See Full Guide → docs/USAGE_AND_TESTS.md](docs/USAGE_AND_TESTS.md)**

> 📎 **Heads up:** If the link below doesn't work on GitHub's homepage,  
>  click into the README file or manually open: `docs/USAGE_AND_TESTS.md`


---

## 🤝 Contributing

Contributions are welcome!

Feel free to open an issue or pull request if you:

- Add new summarizer engines (e.g. T5, local LLMs)
- Encounter bugs or edge cases
- Propose design improvements (e.g. multi-level memory, multi-user support)
- Need streaming / cloud support

---


🧪 Project Status & Friendly Note
ℹ️ Note from the developer:
This project is developed and maintained by an individual beginner in AI system design.
While the memory rotation logic has been carefully implemented and tested in isolation,
it has not yet been integrated or benchmarked with actual AI language models (e.g., OpenAI, LLaMA, etc.).

I’m sharing this plugin as a lightweight, modular base for anyone exploring memory mechanisms in AI dialogue.
If you have feedback, suggestions, or real-world use cases, I’d greatly appreciate your insight!

Feel free to open an Issue or contribute via Pull Request.

Thank you for taking a look 🙏


## 📄 License

Released under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)** License.  
See [LICENSE](./LICENSE) for full terms.

> This package is officially maintained by **YZXY6151**.  
> Any unofficial versions or derivatives **must** retain attribution and **clearly indicate changes**.  
> Commercial use is **not permitted** without explicit permission.

© 2025 YZXY6151 — DualDB Memory Plugin  
All rights reserved under CC BY-NC-SA 4.0. For non-commercial use only.

