import json
from typing import Dict, List, Any
from nexus.utils import NexusLLM, get_logger

logger = get_logger(__name__)

class LLMDebateSystem:
    """
    Three LLM personas debate whether an event is malicious.
    """

    def __init__(self, max_rounds: int = 3):
        self.max_rounds = max_rounds
        self.llm = NexusLLM.get_debate_llm()
        
    def debate(self, suspicious_event: Dict, context: Dict = None) -> Dict:
        """
        Multi-round debate between Prosecutor, Defense, and Judge.
        
        Args:
            suspicious_event: The event in question.
            context: Additional context like past events or alerts.
            
        Returns:
            Dict containing verdict, confidence, reasoning, and rounds.
        """
        rounds = []
        event_str = json.dumps(suspicious_event, indent=2)
        context_str = json.dumps(context, indent=2) if context else "None"
        
        prosecutor_sys = (
            "You are a cyber security Prosecutor. Argue why the provided event is malicious. "
            "Cite specific MITRE ATT&CK techniques. Provide strong evidence."
        )
        defense_sys = (
            "You are a cyber security Defense attorney. Argue why the provided event is benign. "
            "Suggest legitimate explanations or administrative activities that cause this."
        )
        judge_sys = (
            "You are a cyber security Judge. Weigh the arguments from the Prosecutor and Defense. "
            "You must return a JSON response with keys: 'verdict' (malicious, benign, or suspicious), "
            "'confidence' (float 0.0 to 1.0), and 'reasoning' (string explaining your decision)."
        )
        
        current_context = f"Event:\n{event_str}\n\nContext:\n{context_str}\n"
        
        for i in range(self.max_rounds):
            prosecutor_prompt = f"Round {i+1} Context:\n{current_context}\nMake your case for why this is malicious."
            prosecutor_arg = self.llm.invoke(prosecutor_sys, prosecutor_prompt)
            
            current_context += f"\nProsecutor Argument:\n{prosecutor_arg}\n"
            
            defense_prompt = f"Round {i+1} Context:\n{current_context}\nMake your case for why this is benign."
            defense_arg = self.llm.invoke(defense_sys, defense_prompt)
            
            current_context += f"\nDefense Argument:\n{defense_arg}\n"
            
            rounds.append({
                "round": i + 1,
                "prosecutor": prosecutor_arg,
                "defense": defense_arg
            })
            
        judge_prompt = f"Review the arguments and make a final verdict:\n\n{current_context}"
        try:
            verdict_json = self.llm.invoke_structured(judge_sys, judge_prompt)
            verdict = verdict_json.get("verdict", "suspicious").lower()
            confidence = float(verdict_json.get("confidence", 0.5))
            reasoning = verdict_json.get("reasoning", "No reasoning provided.")
        except Exception as e:
            logger.error(f"Failed to parse judge verdict: {e}")
            verdict = "suspicious"
            confidence = 0.5
            reasoning = "Failed to parse judge verdict due to error."
            
        return {
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": reasoning,
            "rounds": rounds
        }

    def quick_assess(self, event: Dict) -> Dict:
        """
        Single-turn fast assessment.
        
        Args:
            event: Event to assess.
            
        Returns:
            Dict containing verdict, confidence, and reasoning.
        """
        event_str = json.dumps(event, indent=2)
        judge_sys = (
            "You are a cyber security analyst. Perform a quick assessment of this event. "
            "You must return a JSON response with keys: 'verdict' (malicious, benign, or suspicious), "
            "'confidence' (float 0.0 to 1.0), and 'reasoning' (string explaining your decision)."
        )
        prompt = f"Assess the following event:\n{event_str}"
        
        try:
            verdict_json = self.llm.invoke_structured(judge_sys, prompt)
            verdict = verdict_json.get("verdict", "suspicious").lower()
            confidence = float(verdict_json.get("confidence", 0.5))
            reasoning = verdict_json.get("reasoning", "No reasoning provided.")
        except Exception as e:
            logger.error(f"Failed to parse quick assess verdict: {e}")
            verdict = "suspicious"
            confidence = 0.5
            reasoning = "Failed to parse verdict due to error."
            
        return {
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": reasoning
        }
