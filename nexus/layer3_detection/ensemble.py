from typing import Dict, List, Any
from .sigma_engine import SigmaDetectionEngine
from .gnn_detector import GNNAnomalyDetector
from .llm_debate import LLMDebateSystem
from nexus.utils import get_logger

logger = get_logger(__name__)

class TriBrainEnsemble:
    """
    Orchestrates SigmaEngine, GNNAnomalyDetector, and LLMDebateSystem.
    Computes a weighted ensemble score to determine overall verdict.
    """

    def __init__(self, sigma_engine: SigmaDetectionEngine, gnn_detector: GNNAnomalyDetector, llm_debate: LLMDebateSystem, weights: Dict[str, float] = None):
        self.sigma = sigma_engine
        self.gnn = gnn_detector
        self.llm = llm_debate
        self.weights = weights or {"sigma": 0.4, "gnn": 0.3, "llm": 0.3}
        self.stats = {
            "total_evaluated": 0,
            "verdicts": {"benign": 0, "suspicious": 0, "malicious": 0},
            "accuracy": {"sigma": 0.0, "gnn": 0.0, "llm": 0.0} # Placeholder for actual accuracy tracking
        }

    def evaluate(self, log_event: Dict, graph_data: Dict = None, context: Dict = None) -> Dict:
        """
        Run all three brains, compute weighted score.
        If sigma or gnn flags something, trigger full debate; otherwise quick_assess.
        """
        self.stats["total_evaluated"] += 1
        
        # 1. Sigma Engine
        sigma_matches = self.sigma.evaluate(log_event)
        sigma_score = 1.0 if sigma_matches else 0.0
        
        # 2. GNN Detector
        gnn_score = 0.0
        # The new GNN evaluates batch features, so we can pass single event as list
        anomalies = self.gnn.analyze([log_event])
        for anomaly in anomalies:
            if anomaly["node"] == log_event.get("host") or anomaly["node"] == log_event.get("source_host"):
                # Scale the anomaly score for the ensemble (typically 0.0 to 1.0)
                gnn_score = min(1.0, anomaly["anomaly_score"] / max(self.gnn.threshold, 0.1))
                break

        # Determine if debate is needed
        needs_debate = sigma_score > 0 or gnn_score > 0.5
        
        # 3. LLM Evaluation
        if needs_debate:
            llm_result = self.llm.debate(log_event, context)
        else:
            llm_result = self.llm.quick_assess(log_event)
            
        llm_verdict = llm_result.get("verdict", "benign")
        if llm_verdict == "malicious":
            llm_score = 1.0
        elif llm_verdict == "suspicious":
            llm_score = 0.5
        else:
            llm_score = 0.0
            
        # Combine scores
        ensemble_score = (
            sigma_score * self.weights["sigma"] +
            gnn_score * self.weights["gnn"] +
            llm_score * self.weights["llm"]
        )
        
        # Determine overall verdict
        if ensemble_score > 0.7:
            final_verdict = "MALICIOUS"
        elif ensemble_score > 0.4:
            final_verdict = "SUSPICIOUS"
        else:
            final_verdict = "BENIGN"
            
        self.stats["verdicts"][final_verdict.lower()] = self.stats["verdicts"].get(final_verdict.lower(), 0) + 1

        return {
            "verdict": final_verdict,
            "ensemble_score": ensemble_score,
            "sigma_result": sigma_matches,
            "gnn_result": gnn_score,
            "llm_result": llm_result,
            "reasoning": f"Ensemble score: {ensemble_score:.2f}. LLM reasoning: {llm_result.get('reasoning')}"
        }

    def evaluate_batch(self, events: List[Dict], graph_data: Dict = None) -> List[Dict]:
        """Evaluate a batch of log events."""
        results = []
        for event in events:
            results.append(self.evaluate(event, graph_data))
        return results

    def get_detection_stats(self) -> Dict:
        """Get total evaluated, by verdict, per-brain accuracy."""
        return self.stats

    def adjust_weights(self, performance_data: Dict):
        """
        Rebalance brain weights based on accuracy in performance_data.
        Expects performance_data to map brain name to accuracy (0.0 to 1.0).
        """
        total_accuracy = sum(performance_data.values())
        if total_accuracy > 0:
            for brain in self.weights:
                if brain in performance_data:
                    self.weights[brain] = performance_data[brain] / total_accuracy
            logger.info(f"Adjusted weights: {self.weights}")
        else:
            logger.warning("Total accuracy is 0, cannot adjust weights.")
