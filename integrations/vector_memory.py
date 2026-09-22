"""
NEXUS — Vector Memory Engine
SQLite + TF-IDF cosine similarity vector store.
Dropin replacement for ChromaDB, ARM64-safe, zero native deps.

Stores attacker actions, defender detections, and evolution insights
as searchable semantic vectors.
"""
from __future__ import annotations

import json
import math
import re
import sqlite3
import time
import uuid
from collections import Counter
from pathlib import Path
from typing import Optional


# ── TF-IDF vectoriser (pure Python) ─────────────────────────────────────────

def _tokenise(text: str) -> list[str]:
    return re.findall(r'[a-zA-Z0-9]+', text.lower())


def _tfidf(doc: str, corpus: list[str]) -> dict[str, float]:
    tokens = _tokenise(doc)
    if not tokens:
        return {}
    tf = Counter(tokens)
    n = len(tokens)
    tf_norm = {t: c / n for t, c in tf.items()}
    N = len(corpus)
    idf = {}
    for term in tf_norm:
        df = sum(1 for d in corpus if term in _tokenise(d))
        idf[term] = math.log((N + 1) / (df + 1)) + 1.0
    return {t: tf_norm[t] * idf[t] for t in tf_norm}


def _cosine(v1: dict, v2: dict) -> float:
    common = set(v1) & set(v2)
    if not common:
        return 0.0
    dot = sum(v1[k] * v2[k] for k in common)
    mag1 = math.sqrt(sum(x * x for x in v1.values()))
    mag2 = math.sqrt(sum(x * x for x in v2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


# ── Vector Memory ────────────────────────────────────────────────────────────

class VectorMemory:
    """
    Persistent semantic memory store for NEXUS agents.

    Usage:
        mem = VectorMemory(agent_id="NOVA")
        mem.store("Used T1078 on DC-001, was detected by SIGMA")
        results = mem.search("credential abuse on domain controller", top_k=3)
    """

    def __init__(self, agent_id: str = "global",
                 db_path: str = "data/nexus_memory.db"):
        self.agent_id = agent_id
        self.db_path  = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id          TEXT PRIMARY KEY,
                    agent_id    TEXT NOT NULL,
                    content     TEXT NOT NULL,
                    metadata    TEXT DEFAULT '{}',
                    timestamp   REAL NOT NULL,
                    category    TEXT DEFAULT 'general'
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_agent ON memories(agent_id)"
            )
            conn.commit()

    # ── Write ─────────────────────────────────────────────────────────────────

    def store(self, content: str, metadata: dict | None = None,
              category: str = "action") -> str:
        """Store a memory entry. Returns the memory ID."""
        mem_id = str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO memories VALUES (?,?,?,?,?,?)",
                (mem_id, self.agent_id, content,
                 json.dumps(metadata or {}), time.time(), category)
            )
            conn.commit()
        return mem_id

    def store_attack(self, technique: str, host: str, stealth: str,
                     detected: bool, rationale: str = "") -> str:
        """Convenience: store an attack action."""
        content = (
            f"Technique {technique} on {host} stealth={stealth} "
            f"detected={detected} rationale={rationale}"
        )
        return self.store(content, metadata={
            "technique": technique, "host": host,
            "stealth": stealth, "detected": detected,
        }, category="attack")

    def store_detection(self, technique: str, host: str, agent: str,
                        sigma_rule: str = "") -> str:
        """Convenience: store a detection event."""
        content = (
            f"Detection: {agent} {technique} on {host} "
            f"rule={sigma_rule}"
        )
        return self.store(content, metadata={
            "technique": technique, "host": host,
            "agent": agent, "sigma_rule": sigma_rule,
        }, category="detection")

    # ── Read ──────────────────────────────────────────────────────────────────

    def search(self, query: str, top_k: int = 5,
               category: str | None = None) -> list[dict]:
        """
        Semantic search over stored memories.
        Returns list of {content, metadata, score, timestamp}.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if category:
                rows = conn.execute(
                    "SELECT * FROM memories WHERE agent_id=? AND category=?"
                    " ORDER BY timestamp DESC LIMIT 200",
                    (self.agent_id, category)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM memories WHERE agent_id=?"
                    " ORDER BY timestamp DESC LIMIT 200",
                    (self.agent_id,)
                ).fetchall()

        if not rows:
            return []

        corpus = [r["content"] for r in rows]
        q_vec  = _tfidf(query, corpus)
        scored = []
        for row in rows:
            d_vec = _tfidf(row["content"], corpus)
            score = _cosine(q_vec, d_vec)
            scored.append({
                "id":        row["id"],
                "content":   row["content"],
                "metadata":  json.loads(row["metadata"]),
                "category":  row["category"],
                "timestamp": row["timestamp"],
                "score":     round(score, 4),
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def recent(self, n: int = 10, category: str | None = None) -> list[dict]:
        """Return most recent n memories."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if category:
                rows = conn.execute(
                    "SELECT * FROM memories WHERE agent_id=? AND category=?"
                    " ORDER BY timestamp DESC LIMIT ?",
                    (self.agent_id, category, n)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM memories WHERE agent_id=?"
                    " ORDER BY timestamp DESC LIMIT ?",
                    (self.agent_id, n)
                ).fetchall()
        return [{
            "id": r["id"], "content": r["content"],
            "metadata": json.loads(r["metadata"]),
            "category": r["category"], "timestamp": r["timestamp"],
        } for r in rows]

    def count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM memories WHERE agent_id=?",
                (self.agent_id,)
            ).fetchone()[0]

    def clear(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM memories WHERE agent_id=?",
                         (self.agent_id,))
            conn.commit()

    def summary(self) -> str:
        cats = {}
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT category, COUNT(*) as n FROM memories"
                " WHERE agent_id=? GROUP BY category",
                (self.agent_id,)
            ).fetchall()
        for r in rows:
            cats[r[0]] = r[1]
        total = sum(cats.values())
        return f"[Memory:{self.agent_id}] {total} entries — {cats}"


# ── Global memory registry ────────────────────────────────────────────────────

_registry: dict[str, VectorMemory] = {}


def get_memory(agent_id: str,
               db_path: str = "data/nexus_memory.db") -> VectorMemory:
    """Get or create a VectorMemory for a given agent ID."""
    if agent_id not in _registry:
        _registry[agent_id] = VectorMemory(agent_id=agent_id, db_path=db_path)
    return _registry[agent_id]


def get_global_memory(db_path: str = "data/nexus_memory.db") -> VectorMemory:
    return get_memory("global", db_path)
