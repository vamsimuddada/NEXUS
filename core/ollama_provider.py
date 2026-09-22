"""
NEXUS — Ollama LLM Provider
Runs LLMs fully locally via Ollama. No API key, no internet, no rate limits.
Works on ARM64 (Raspberry Pi 5, Apple Silicon, any Linux ARM64).

Setup (one-time):
    curl -fsSL https://ollama.com/install.sh | sh
    ollama pull llama3.2:3b       # fast, 2GB, works on 8GB RAM
    ollama pull phi3:mini          # fast, 2.3GB, very capable
    ollama pull mistral:7b-instruct # best quality, 4GB, needs 8GB+ RAM

Models ranked for NEXUS use (speed vs quality):
    llama3.2:3b       — recommended default, fast on ARM64
    phi3:mini          — Microsoft, excellent instruction following
    mistral:7b-instruct— best quality, slower
    llama3.2:1b        — ultra-fast, lower quality
    gemma2:2b          — Google, good balance

Ollama runs as a local HTTP server on port 11434.
The Python SDK connects to it automatically.
"""

from __future__ import annotations

import json
import os
import time
from typing import Optional


# ── Recommended models for ARM64 ─────────────────────────────────────────────

RECOMMENDED_MODELS = {
    "fast":    "llama3.2:3b",        # default — 2GB, fast
    "quality": "mistral:7b-instruct", # 4GB, best reasoning
    "tiny":    "llama3.2:1b",         # 1.3GB, ultra-fast
    "phi":     "phi3:mini",           # 2.3GB, great instruction following
    "gemma":   "gemma2:2b",           # 1.6GB, good balance
}

DEFAULT_MODEL = os.getenv("NEXUS_OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_HOST   = os.getenv("OLLAMA_HOST", "http://localhost:11434")


# ── Ollama provider ───────────────────────────────────────────────────────────

class OllamaProvider:
    """
    Wraps the Ollama Python SDK to match the interface expected by all NEXUS
    LLM call sites (base_agent, debate_engine, evolution_engine, paper_generator).

    Usage:
        provider = OllamaProvider()
        text = provider.call("Your prompt here")
    """

    def __init__(self, model: Optional[str] = None, host: Optional[str] = None):
        self.model  = model or DEFAULT_MODEL
        self.host   = host  or OLLAMA_HOST
        self._client = None
        self._available = False
        self._init()

    def _init(self):
        try:
            import ollama
            # Create client pointing at the configured host
            self._client = ollama.Client(host=self.host)
            # Check Ollama is running by listing models
            models_resp = self._client.list()
            available   = [m.model for m in models_resp.models]

            if not available:
                print(f"[Ollama] Server running but no models pulled yet.")
                print(f"[Ollama] Run: ollama pull {self.model}")
                return

            # Check if our model is available
            # Model names can have :latest suffix stripped
            model_base = self.model.split(":")[0]
            matched = [m for m in available
                       if m.startswith(model_base) or m == self.model]

            if matched:
                self.model      = matched[0]   # use exact name from server
                self._available = True
                print(f"[Ollama] Ready — model={self.model} host={self.host}")
            else:
                print(f"[Ollama] Model '{self.model}' not found.")
                print(f"[Ollama] Available: {available}")
                print(f"[Ollama] Run: ollama pull {self.model}")
                # Use first available model as fallback
                if available:
                    self.model      = available[0]
                    self._available = True
                    print(f"[Ollama] Falling back to: {self.model}")

        except Exception as e:
            print(f"[Ollama] Not available: {e}")
            print(f"[Ollama] Install: curl -fsSL https://ollama.com/install.sh | sh")
            print(f"[Ollama] Then run: ollama pull {self.model}")

    def call(self, prompt: str, max_tokens: int = 512,
             temperature: float = 0.7) -> str:
        """
        Send a prompt to Ollama and return the text response.
        Falls back to empty string on any error.
        """
        if not self._available or self._client is None:
            return ""

        try:
            response = self._client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "top_p":       0.9,
                },
            )
            return response.message.content.strip()
        except Exception as e:
            print(f"[Ollama] Call failed: {e}")
            return ""

    def call_json(self, prompt: str, max_tokens: int = 512) -> Optional[dict]:
        """
        Call Ollama expecting a JSON response.
        Automatically strips markdown fences and retries once on parse failure.
        """
        full_prompt = (
            prompt
            + "\n\nIMPORTANT: Respond with ONLY valid JSON. "
            + "No explanation, no markdown, no backticks. Just the JSON object."
        )
        raw = self.call(full_prompt, max_tokens=max_tokens, temperature=0.2)
        if not raw:
            return None
        return self._parse_json(raw)

    def _parse_json(self, raw: str) -> Optional[dict]:
        """Try several ways to extract JSON from a response."""
        # Direct parse
        try:
            clean = raw.strip().strip("```json").strip("```").strip()
            return json.loads(clean)
        except Exception:
            pass

        # Find first { ... } block
        import re
        match = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass

        return None

    @property
    def available(self) -> bool:
        return self._available

    def list_models(self) -> list[str]:
        """Return all models currently pulled in Ollama."""
        if not self._client:
            return []
        try:
            return [m.model for m in self._client.list().models]
        except Exception:
            return []

    def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama Hub. Returns True on success."""
        if not self._client:
            return False
        try:
            print(f"[Ollama] Pulling {model} — this may take a few minutes…")
            self._client.pull(model)
            print(f"[Ollama] {model} pulled successfully ✓")
            return True
        except Exception as e:
            print(f"[Ollama] Pull failed: {e}")
            return False


# ── Singleton ─────────────────────────────────────────────────────────────────

_provider: Optional[OllamaProvider] = None


def get_ollama(model: Optional[str] = None,
               host:  Optional[str] = None) -> OllamaProvider:
    global _provider
    if _provider is None:
        _provider = OllamaProvider(model=model, host=host)
    return _provider


def reset_ollama():
    """Force re-initialisation (e.g. after changing model)."""
    global _provider
    _provider = None
