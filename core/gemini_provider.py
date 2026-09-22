"""
NEXUS — Gemini LLM Provider
Drop-in replacement for the Anthropic provider.
Uses Google Gemini API (free tier: 1500 req/day, no credit card).

Free tier limits (as of 2024):
  gemini-2.0-flash-lite : 1500 req/day, 1M tokens/min
  gemini-2.0-flash      : 1500 req/day, 1M tokens/min
  gemini-1.5-flash      : 1500 req/day, 1M tokens/min
  gemini-1.5-flash-8b   : 1500 req/day, 4M tokens/min

Get your free API key at: https://aistudio.google.com/apikey
No credit card required.
"""

from __future__ import annotations

import json
import os
import time
from typing import Optional


# ── Rate limiting (stay within free tier) ────────────────────────────────────

_last_call_time: float = 0.0
_min_interval:   float = 0.5   # 500ms between calls — well within free limits


def _rate_limit():
    global _last_call_time
    elapsed = time.time() - _last_call_time
    if elapsed < _min_interval:
        time.sleep(_min_interval - elapsed)
    _last_call_time = time.time()


# ── Gemini client ─────────────────────────────────────────────────────────────

class GeminiProvider:
    """
    Wraps the Google Gemini API to match the interface expected by NEXUS.

    Usage:
        provider = GeminiProvider()
        text = provider.call("Your prompt here")
    """

    DEFAULT_MODEL = "gemini-2.0-flash-lite"   # fastest free model

    def __init__(self, api_key: Optional[str] = None,
                 model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model   = model   or os.getenv("NEXUS_GEMINI_MODEL", self.DEFAULT_MODEL)
        self._client = None
        self._init()

    def _init(self):
        if not self.api_key:
            print("[Gemini] No API key — falling back to mock")
            return
        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            print(f"[Gemini] Initialised — model={self.model}")
        except Exception as e:
            print(f"[Gemini] Init failed: {e}")

    def call(self, prompt: str, max_tokens: int = 512,
             temperature: float = 0.7) -> str:
        """
        Send a prompt to Gemini and return the text response.
        Falls back to empty string on any error (callers handle fallback).
        """
        if not self._client:
            return ""

        _rate_limit()

        try:
            from google.genai import types
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )
            return response.text.strip() if response.text else ""
        except Exception as e:
            print(f"[Gemini] API error: {e}")
            return ""

    def call_json(self, prompt: str, max_tokens: int = 512) -> Optional[dict]:
        """
        Call Gemini expecting a JSON response.
        Automatically strips markdown fences if present.
        """
        raw = self.call(prompt + "\n\nRespond with ONLY valid JSON. No markdown.",
                        max_tokens=max_tokens, temperature=0.3)
        if not raw:
            return None
        try:
            clean = raw.strip().strip("```json").strip("```").strip()
            return json.loads(clean)
        except Exception:
            return None

    @property
    def available(self) -> bool:
        return self._client is not None


# ── Singleton (shared across all agents in one run) ───────────────────────────

_provider: Optional[GeminiProvider] = None


def get_gemini(api_key: Optional[str] = None) -> GeminiProvider:
    global _provider
    if _provider is None:
        _provider = GeminiProvider(api_key=api_key)
    return _provider
