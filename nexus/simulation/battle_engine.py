import uuid
import os
from typing import Dict, List, Optional
from datetime import datetime

from nexus.utils import get_logger, NexusDB
from nexus.layer1_digital_twin.enterprise import DigitalTwinEnterprise
from nexus.layer2_attacker_council import AGENT_REGISTRY, AttackerCommChannel
from nexus.layer3_detection.sigma_engine import SigmaDetectionEngine
from nexus.layer3_detection.gnn_detector import GNNAnomalyDetector
from nexus.layer3_detection.llm_debate import LLMDebateSystem
from nexus.layer3_detection.ensemble import TriBrainEnsemble
from nexus.layer4_evolution.gap_analyzer import GapAnalyzer
from nexus.layer4_evolution.rule_generator import SigmaRuleGenerator
from nexus.layer4_evolution.model_trainer import IncrementalModelTrainer
from nexus.layer4_evolution.psychology_memory import AttackerPsychologyMemory
from nexus.layer5_soar.response_engine import AutomatedResponseEngine
from nexus.layer5_soar.honeypot import AdaptiveHoneypot
from nexus.layer6_scoring.elo_system import EloScoring
from nexus.layer6_scoring.replay import CampaignReplay
from nexus.layer7_research.stix_generator import StixBundleGenerator

from .results_collector import ResultsCollector
from .scenario_loader import ScenarioLoader

logger = get_logger(__name__)

class BattleEngine:
    """The core orchestrator for the NEXUS cybersecurity simulation platform."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.sim_id = str(uuid.uuid4())
        self.results_collector = ResultsCollector()
        self.db = NexusDB()
        
        self.environment = None
        self.comm_channel = None
        
        self.sigma_engine = None
        self.gnn_detector = None
        self.llm_debate = None
        self.tri_brain = None
        
        self.gap_analyzer = None
        self.sigma_generator = None
        self.incremental_trainer = None
        self.psychology_memory = None
        
        self.response_engine = None
        self.adaptive_honeypot = None
        
        self.elo_scoring = None
        self.campaign_replay = None
        self.stix_generator = None
        
        self.attackers = []
        
    def setup_simulation(self, num_employees: int = 100, num_subnets: int = 5, **kwargs):
        """Initializes all layers of the simulation."""
        logger.info(f"Setting up simulation {self.sim_id}")
        
        # Layer 1
        self.environment = DigitalTwinEnterprise(num_employees=num_employees, num_subnets=num_subnets)
        self.environment.generate()
        
        # Layer 2
        self.comm_channel = AttackerCommChannel()
        
        # Layer 3
        rules_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'layer3_detection', 'rules', 'base_rules')
        if not os.path.exists(rules_path):
            os.makedirs(rules_path, exist_ok=True)
            
        self.sigma_engine = SigmaDetectionEngine()
        self.sigma_engine.load_rules(rules_path)
        self.gnn_detector = GNNAnomalyDetector()
        
        baseline_logs = self.environment.logs
        if hasattr(self, 'gnn_detector'):
            topology = getattr(self.environment, 'network', None).graph if hasattr(self.environment, 'network') else None
            self.gnn_detector.train(baseline_logs, topology)
        
        self.llm_debate = LLMDebateSystem()
        self.tri_brain = TriBrainEnsemble(self.sigma_engine, self.gnn_detector, self.llm_debate)
        
        # Layer 4
        self.gap_analyzer = GapAnalyzer()
        self.sigma_generator = SigmaRuleGenerator()
        self.incremental_trainer = IncrementalModelTrainer()
        self.psychology_memory = AttackerPsychologyMemory()
        
        # Layer 5
        self.response_engine = AutomatedResponseEngine()
        self.adaptive_honeypot = AdaptiveHoneypot()
        self.elo_scoring = EloScoring()
        self.campaign_replay = CampaignReplay()
        self.stix_generator = StixBundleGenerator()
        
    def run_simulation(self, num_rounds: int = 20, attackers: List[str] = None, scenario_name: str = None):
        """Executes the simulation loop."""
        logger.info(f"Running simulation {self.sim_id}")
        
        if scenario_name:
            scenarios = ScenarioLoader.list_scenarios()
            if scenario_name in scenarios:
                scenario = scenarios[scenario_name]
                attackers = scenario.get('attackers', attackers)
                num_rounds = scenario.get('rounds', num_rounds)
            else:
                logger.warning(f"Scenario {scenario_name} not found. Using default arguments.")
                
        if not attackers:
            attackers_names = list(AGENT_REGISTRY.keys())
            if not attackers_names:
                raise ValueError("No attackers available in AGENT_REGISTRY")
            attackers = [attackers_names[0]]
            
        # Instantiate attacker agents
        self.attackers = []
        for attacker_name in attackers:
            if attacker_name in AGENT_REGISTRY:
                agent_class = AGENT_REGISTRY[attacker_name]

                import yaml
                import os
                profile = {'name': attacker_name}
                try:
                    with open(os.path.join('config', 'attacker_profiles.yaml'), 'r') as f:
                        attackers_cfg = yaml.safe_load(f).get('attackers', [])
                        for a in attackers_cfg:
                            if a.get('name') == attacker_name or a.get('id') == attacker_name:
                                profile = a
                                profile['name'] = a.get('name', attacker_name)
                                profile['personality_traits'] = {
                                    'aggression': a.get('aggression_level', 0.5),
                                    'stealth': a.get('stealth_level', 0.5),
                                    'patience': a.get('patience_level', 0.5),
                                    'cooperation': a.get('cooperation_tendency', 0.5)
                                }
                                break
                except Exception as e:
                    logger.warning(f"Could not load profile for {attacker_name}: {e}")
                
                # Some agents take (id, profile), some might take (name, profile)
                agent = agent_class(self.sim_id, profile)

                self.attackers.append(agent)
            else:
                logger.warning(f"Attacker {attacker_name} not found in registry.")
                
        # Core Loop
        all_new_logs = []
        all_ground_truth = []
        
        for round_num in range(num_rounds):
            logger.info(f"Starting Round {round_num}")
            self.results_collector.record(self.sim_id, round_num, "round_start", {"round": round_num})
            
            # Attackers act
            round_logs = []
            for attacker in self.attackers:
                env_state = self.environment.get_state() if hasattr(self.environment, 'get_state') else {}
                action = attacker.plan_action(env_state)
                result = attacker.execute_action(action, self.environment)
                
                if result.get("success", False):
                    new_logs = self.environment.generate_logs_for_action(action) if hasattr(self.environment, 'generate_logs_for_action') else []
                    round_logs.extend(new_logs)
                    
                    truth = {"action": action, "timestamp": datetime.now().isoformat(), "attacker": attacker.name if hasattr(attacker, 'name') else str(attacker)}
                    all_ground_truth.append(truth)
                    
                    self.results_collector.record(self.sim_id, round_num, "attacker_action", result)
                    self.campaign_replay.record_event("attacker_action", result)
                    
                # Attacker communication
                messages = self.comm_channel.receive(attacker.name if hasattr(attacker, 'name') else str(attacker))
                for msg in messages:
                    if hasattr(attacker, 'process_message'):
                        attacker.process_message(msg)
                    
            all_new_logs.extend(round_logs)
            
            # Defensive Evaluation (Layer 3)
            for log in round_logs:
                detection_result = self.tri_brain.evaluate(log)
                
                if detection_result.get("is_malicious", False):
                    self.results_collector.record(self.sim_id, round_num, "detection", detection_result)
                    
                    # Layer 5: Automated Response
                    response = self.response_engine.mitigate(detection_result)
                    self.results_collector.record(self.sim_id, round_num, "response", response)
                    
                    self.adaptive_honeypot.deploy_decoy(detection_result)
                    
                    for attacker in self.attackers:
                        if hasattr(attacker, 'observe_detection'):
                            attacker.observe_detection(detection_result)
                        
                    self.campaign_replay.record_event("defense_action", response)
                    
            # Elo update
            for attacker in self.attackers:
                attacker_id = attacker.name if hasattr(attacker, 'name') else str(attacker)
                self.elo_scoring.update_ratings(attacker_id, {"detected": False, "blocked": False})
            
            self.results_collector.record(self.sim_id, round_num, "round_end", {"round": round_num})
            
        # Post-Simulation Analysis
        logger.info("Running post-simulation analysis")
        
        # Layer 4 Gap Analysis
        detections = self.results_collector.get_simulation_results(self.sim_id)
        detection_events = [d['data'] for d in detections if d['event_type'] == 'detection']
        
        gaps = self.gap_analyzer.analyze(all_ground_truth, detection_events)
        
        for gap in gaps.get('false_negatives', []):
            new_rule = self.sigma_generator.generate_rule(gap)
            if new_rule:
                logger.info("Generated new Sigma rule to cover gap")
                
        for attacker in self.attackers:
            if hasattr(self.psychology_memory, 'update_memory'):
                self.psychology_memory.update_memory(attacker)
            
        # Add new logs to training data (assume non-malicious initially if not in detections)
        labels = [any(log['log_id'] == det['log_id'] for det in detection_events) for log in all_new_logs]
        self.incremental_trainer.update_training_data(all_new_logs, labels)
        
        if self.incremental_trainer.should_retrain():
            logger.info("Retraining GNN detector...")
            self.incremental_trainer.fine_tune(self.gnn_detector)
            
    def get_results(self) -> Dict:
        """Gets full results of the current simulation."""
        events = self.results_collector.get_simulation_results(self.sim_id)
        
        # Extract metadata for research reporting (STIX)
        techniques = list({e.get('data', {}).get('attack_technique_id') for e in events if e.get('event_type') == 'attacker_action' and isinstance(e.get('data'), dict) and e.get('data', {}).get('attack_technique_id')})
        
        return {
            "sim_id": self.sim_id,
            "attacker_id": "Mixed_Agents" if len(self.attackers) > 1 else (self.attackers[0].name if self.attackers else "Unknown"),
            "techniques": techniques if techniques else ["T1000"],
            "events": events,
            "elo_scores": {}
        }
        
    def get_summary(self) -> str:
        """Gets a brief summary of the simulation results."""
        results = self.get_results()
        num_events = len(results["events"])
        return f"Simulation {self.sim_id} completed. Total recorded events: {num_events}."
