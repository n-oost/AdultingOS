"""
FormKnowledgeBase: lightweight RAG loader and search for Canadian gov documents.

Loads embeddings from a JSONL file (one JSON object per line) with fields like:
- text: full text content (string)
- title: optional title (string)
- url: optional source URL (string)
- embedding: list[float] (same model for all rows)

Query search attempts to use OpenAI embeddings (text-embedding-3-small) when
OPENAI_API_KEY is configured. If not available, it falls back to a simple
keyword-overlap scoring against title+text.

This module has no numpy/scikit deps by design.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple


DEFAULT_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "embeddings.jsonl")
)


@dataclass
class KBItem:
    text: str
    title: str
    url: Optional[str]
    embedding: Optional[List[float]]
    _norm: Optional[float]


class FormKnowledgeBase:
    def __init__(self, file_path: Optional[str] = None) -> None:
        self.file_path = file_path or DEFAULT_FILE
        self._items: List[KBItem] = []
        self._loaded: bool = False

    # ---------- public API ----------
    def ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._items = self._load_jsonl(self.file_path)
        self._loaded = True

    def search(self, query: str, top_k: int = 5) -> List[Tuple[KBItem, float]]:
        """
        Searches the KB. If query embeddings can be computed (OpenAI), uses cosine
        similarity over vectors. Else uses simple keyword overlap score.
        Returns a list of (item, score) sorted descending.
        """
        self.ensure_loaded()
        if not self._items:
            return []

        q_vec = self._embed_query_or_none(query)
        if q_vec is not None:
            q_norm = _l2norm(q_vec)
            if q_norm == 0.0:
                return []
            scores: List[Tuple[KBItem, float]] = []
            for it in self._items:
                if it.embedding and it._norm and it._norm > 0.0:
                    sim = _dot(q_vec, it.embedding) / (q_norm * it._norm)
                    scores.append((it, float(sim)))
            scores.sort(key=lambda t: t[1], reverse=True)
            return scores[: max(1, top_k)]

        # Lexical fallback
        q_tokens = _tokens(query)
        if not q_tokens:
            return []
        scores: List[Tuple[KBItem, float]] = []
        for it in self._items:
            title_tokens = _tokens(it.title)
            text_tokens = _tokens(it.text[:2000])  # cap to save time
            # title gets higher weight
            overlap = len(q_tokens & title_tokens) * 2 + len(q_tokens & text_tokens)
            # quick length normalization
            denom = 1 + len(title_tokens) * 0.5 + len(text_tokens) * 0.1
            score = overlap / denom
            if score > 0:
                scores.append((it, float(score)))
        scores.sort(key=lambda t: t[1], reverse=True)
        return scores[: max(1, top_k)]

    # ---------- helpers ----------
    def _embed_query_or_none(self, query: str) -> Optional[List[float]]:
        """
        Try OpenAI embeddings if available; otherwise return None to trigger lexical fallback.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        try:
            # openai>=1.x SDK
            from openai import OpenAI  # type: ignore

            client = OpenAI(api_key=api_key)
            model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
            resp = client.embeddings.create(model=model, input=query)
            vec = resp.data[0].embedding  # type: ignore[attr-defined]
            # Ensure it's list[float]
            return [float(x) for x in vec]
        except Exception:
            return None

    def _load_jsonl(self, path: str) -> List[KBItem]:
        if not os.path.exists(path):
            return []
        items: List[KBItem] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                text = str(obj.get("text") or "").strip()
                if not text:
                    continue
                title = (
                    str(obj.get("title") or obj.get("form_id") or obj.get("filename") or "Document").strip()
                )
                url = obj.get("url")
                emb = obj.get("embedding")
                vec: Optional[List[float]] = None
                norm: Optional[float] = None
                if isinstance(emb, list) and emb and all(isinstance(v, (int, float)) for v in emb):
                    vec = [float(v) for v in emb]
                    norm = _l2norm(vec)
                items.append(KBItem(text=text, title=title, url=url, embedding=vec, _norm=norm))
        return items


# ---------- small math/string utils ----------


def _dot(a: Iterable[float], b: Iterable[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _l2norm(v: Iterable[float]) -> float:
    s = sum(x * x for x in v)
    return s ** 0.5


_WORD_RE = re.compile(r"[A-Za-z0-9]+", re.UNICODE)


def _tokens(text: str) -> set[str]:
    if not text:
        return set()
    return {t.lower() for t in _WORD_RE.findall(text)}


def format_results_plain(results: List[Tuple[KBItem, float]]) -> str:
    """Return a human-friendly plain text list for chat/mobile UIs."""
    if not results:
        return "No matching documents."
    lines: List[str] = []
    for it, score in results:
        url_part = f" – {it.url}" if it.url else ""
        lines.append(f"• {it.title} [score {score:.2f}]{url_part}")
    return "\n".join(lines)
