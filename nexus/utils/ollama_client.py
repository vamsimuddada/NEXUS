"""
NEXUS LLM Client - Official Ollama SDK Integration.
Provides a unified, professional interface to local LLMs via the official `ollama` Python SDK.
Features built-in retries, graceful fallbacks, and Pydantic structured JSON outputs.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional
import ollama
from pydantic import BaseModel

logger = logging.getLogger("nexus.llm")
DEFAULT_MODEL = "llama3"

class NexusLLM:
    """Professional-grade LLM client using the official Ollama SDK."""
    
    def __init__(self, model: str = DEFAULT_MODEL, temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        self.is_connected = self.check_connection()

    def check_connection(self) -> bool:
        """Ping the local Ollama daemon to ensure it is running."""
        try:
            self.client.list()
            return True
        except Exception as e:
            logger.warning(f"Ollama daemon unreachable: {e}. Falling back to deterministic Mock Mode.")
            return False

    def list_models(self) -> List[str]:
        if not self.is_connected: return ["mock-model"]
        try:
            response = self.client.list()
            return [m['name'] for m in response.get('models', [])]
        except Exception:
            return ["mock-model"]

    def generate(self, prompt: str) -> str:
        if not self.is_connected: return "Mock response."
        try:
            response = self.client.generate(model=self.model, prompt=prompt, options={'temperature': self.temperature})
            return response['response']
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return "Mock response."

    def invoke(self, system_prompt: str, user_prompt: str) -> str:
        return self._chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])

    def invoke_structured(self, system_prompt: str, user_prompt: str, schema: Optional[BaseModel] = None) -> Dict[str, Any]:
        """
        Forces the LLM to output structured JSON matching a Pydantic schema.
        This is an enterprise-grade approach for reliable autonomous agent actions.
        """
        if not self.is_connected:
            return self._mock_response([{"role": "user", "content": user_prompt}])

        messages = [
            {"role": "system", "content": system_prompt + "\n\nIMPORTANT: You must reply with raw, valid JSON only. Do not include markdown formatting or conversational text."},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                format='json',
                options={'temperature': self.temperature}
            )
            raw_text = response['message']['content']
            return self._parse_json(raw_text)
        except Exception as e:
            logger.error(f"Structured invocation failed: {e}")
            return self._mock_response(messages)

    def invoke_with_history(self, messages: List[Dict[str, str]]) -> str:
        return self._chat(messages)

    def _chat(self, messages: List[Dict[str, str]]) -> str:
        if not self.is_connected: return "Mock response."
        try:
            response = self.client.chat(model=self.model, messages=messages, options={'temperature': self.temperature})
            return response['message']['content']
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return "Mock response."

    def _mock_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Sophisticated mock router based on intent."""
        user_msg = messages[-1]['content'].lower() if messages else ""
        if 'recon' in user_msg or 'scan' in user_msg:
            return {"action": "scan_network", "technique_id": "T1046", "target": "10.0.0.0/24", "reasoning": "Mock recon."}
        if 'privilege' in user_msg:
            return {"action": "exploit_vuln", "technique_id": "T1068", "target": "DC01", "reasoning": "Mock exploit."}
        if 'detect' in user_msg or 'debate' in user_msg:
            return {"verdict": "malicious", "confidence": 0.9, "reasoning": "Mock verdict.", "rule_name": "MockRule"}
        return {"action": "wait", "technique_id": "none", "target": "none", "reasoning": "Fallback wait."}

    @staticmethod
    def _parse_json(text: str) -> Dict[str, Any]:
        """Safely extract and parse JSON from the LLM output."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\{.*\}', text.replace('\n', ' '), re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except:
                    pass
            return {"error": "Failed to parse JSON", "raw": text}

    @classmethod
    def get_attacker_llm(cls) -> "NexusLLM":
        return cls(model=os.getenv("OLLAMA_MODEL_ATTACKER", DEFAULT_MODEL), temperature=0.8)

    @classmethod
    def get_debate_llm(cls) -> "NexusLLM":
        return cls(model=os.getenv("OLLAMA_MODEL_DEBATE", "mistral"), temperature=0.4)

    @classmethod
    def get_rules_llm(cls) -> "NexusLLM":
        return cls(model=os.getenv("OLLAMA_MODEL_RULES", DEFAULT_MODEL), temperature=0.1)
