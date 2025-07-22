from .summarizer_base import BaseSummarizer
from typing import List, Tuple, Union

class StubSummarizer(BaseSummarizer):
    def summarize(self, texts: List[str]):
        if not texts:
            return "（空摘要）"
        first_snippet = texts[0][:20].replace("\n", " ").strip()
        summary = f"【摘要】共{len(texts)}句，首句片段：{first_snippet}..."
        return summary  # 注意：只返回字符串，而不是 dict！
