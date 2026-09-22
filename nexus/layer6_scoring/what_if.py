import json
from typing import Dict, List
from nexus.utils import NexusLLM, get_logger

logger = get_logger(__name__)

class WhatIfSimulator:
    """Predictive analysis using LLMs for 'what-if' cybersecurity scenarios."""

    def __init__(self):
        self.llm = NexusLLM()

    def modify_scenario(self, base_sim_data: Dict, modifications: Dict) -> Dict:
        """Mutates a scenario by applying modifications to the base simulation data."""
        scenario = dict(base_sim_data)
        # Deep update scenario with modifications
        for key, value in modifications.items():
            if isinstance(value, dict) and key in scenario and isinstance(scenario[key], dict):
                scenario[key].update(value)
            else:
                scenario[key] = value
        logger.info("Scenario modified successfully.")
        return scenario

    def predict_outcome(self, scenario: Dict) -> Dict:
        """Asks the LLM to predict the outcome of a scenario and returns a structured JSON."""
        system_prompt = (
            "You are an expert cybersecurity simulation predictor. Given the scenario configuration, "
            "predict the likely outcome, success probabilities of the attacker, and defensive efficacy. "
            "Return a JSON object with keys: 'predicted_winner', 'attacker_success_probability', "
            "'key_factors', and 'summary_narrative'."
        )
        user_prompt = f"Scenario:\n{json.dumps(scenario, indent=2)}\nPredict the outcome."
        
        try:
            prediction = self.llm.invoke_structured(system_prompt, user_prompt)
            return prediction
        except Exception as e:
            logger.error(f"Failed to predict outcome: {e}")
            return {"error": str(e)}

    def compare_outcomes(self, scenarios: List[Dict]) -> List[Dict]:
        """Compares the predicted outcomes of multiple scenarios."""
        results = []
        for scenario in scenarios:
            outcome = self.predict_outcome(scenario)
            results.append({
                "scenario_name": scenario.get("name", "Unknown Scenario"),
                "outcome": outcome
            })
        return results
