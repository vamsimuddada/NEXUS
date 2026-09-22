"""
Base Attacker Agent Module.

Implements an advanced ReAct (Reasoning and Acting) framework for the autonomous agents.
Instead of a basic switch-case, the agent uses chain-of-thought to formulate plans
based on its specific persona and the MITRE ATT&CK framework.
"""

import logging
from typing import Any, Dict, List, Optional
from nexus.utils.ollama_client import NexusLLM
from nexus.layer2_attacker_council.communication import AttackerCommChannel
from pydantic import BaseModel, Field

logger = logging.getLogger("nexus.attacker")

class AgentActionSchema(BaseModel):
    """Pydantic schema enforcing strict action outputs from the LLM."""
    thought_process: str = Field(description="Step-by-step reasoning on what to do next based on the environment.")
    action: str = Field(description="The functional action to execute (e.g., 'scan_network', 'exploit_vuln', 'lateral_movement').")
    technique_id: str = Field(description="The exact MITRE ATT&CK ID (e.g., 'T1046').")
    target: str = Field(description="The IP or hostname to target.")
    confidence: float = Field(description="Confidence score in this action (0.0 to 1.0).")

class AttackerAgent:
    """Advanced autonomous attacker agent with persona-driven ReAct loops."""
    
    def __init__(self, agent_id: str, profile: Dict[str, Any]):
        self.agent_id = agent_id
        self.profile = profile
        self.name = profile.get('name', 'Unknown')
        self.archetype = profile.get('archetype', 'Advanced Persistent Threat')
        self.system_prompt = profile.get('system_prompt', 'You are an elite cyber operator.')
        self.personality_traits = profile.get('personality_traits', {
            'aggression': 0.5, 'stealth': 0.5, 'patience': 0.5, 'cooperation': 0.5
        })
        self.preferred_techniques = profile.get('preferred_techniques', ['T1046'])
        self.llm = NexusLLM.get_attacker_llm()
        
        self.current_phase = 'recon'
        self.compromised_hosts = set()
        self.discovered_info = {}
        self.action_history = []
        self.is_detected = False
        self.rounds_active = 0
        
        # Build a robust system context
        self.full_system_prompt = (
            f"You are {self.name}, an {self.archetype} autonomous agent.\n"
            f"Traits: {self.personality_traits}\n"
            f"Preferred MITRE Techniques: {', '.join(self.preferred_techniques)}\n"
            f"Operational Directive: {self.system_prompt}\n\n"
            "You operate using the ReAct (Reasoning and Acting) framework. "
            "Evaluate your current phase, internal state, and environment, then output "
            "a highly tactical plan strictly formatted as a JSON object."
        )

    def reset(self) -> None:
        self.current_phase = 'recon'
        self.compromised_hosts = set()
        self.discovered_info = {}
        self.action_history = []
        self.is_detected = False
        self.rounds_active = 0
        logger.info(f"Agent {self.agent_id} state reset.")

    def plan_action(self, environment_state: dict) -> dict:
        """Formulate the next action using ReAct and structured JSON."""
        user_prompt = (
            f"--- CURRENT SITUATION ---\n"
            f"Phase: {self.current_phase}\n"
            f"Compromised Hosts: {list(self.compromised_hosts)}\n"
            f"Discovered Intelligence: {self.discovered_info}\n"
            f"Environment Status: {environment_state}\n"
            f"Last Action Detected: {self.is_detected}\n\n"
            "Based on the above, plan your next move."
        )
        
        try:
            response = self.llm.invoke_structured(
                system_prompt=self.full_system_prompt,
                user_prompt=user_prompt,
                schema=AgentActionSchema
            )
            
            # Map robust schema back to the engine's expected format
            mapped_action = {
                'action': response.get('action', 'wait'),
                'technique_id': response.get('technique_id', 'T0000'),
                'target': response.get('target', 'unknown'),
                'reasoning': response.get('thought_process', 'No reasoning provided.')
            }
            return mapped_action
            
        except Exception as e:
            logger.error(f"Agent {self.agent_id} planning failed: {e}")
            return {'action': 'wait', 'technique_id': '', 'target': '', 'reasoning': str(e)}

    def execute_action(self, action: dict, digital_twin: Any) -> dict:
        """Execute a planned action against the digital twin."""
        action_type = action.get('action', '')
        technique_id = action.get('technique_id', 'T1046')
        target = action.get('target', 'unknown')
        
        result = {'success': False, 'logs_generated': [], 'details': {}}
        source_host = next(iter(self.compromised_hosts)) if self.compromised_hosts else 'external'
        
        try:
            # We map the conceptual actions to the digital twin's log injection capabilities
            new_logs = digital_twin.inject_attack_logs(technique_id, source_host, target, self.agent_id)
            
            if action_type == 'scan_network':
                self.discovered_info[f"scan_{target}"] = {'status': 'open', 'ports': [80, 443]}
                self.current_phase = 'exploitation'
                    
            elif action_type == 'exploit_vuln':
                self.compromised_hosts.add(target)
                self.current_phase = 'lateral_movement'
                    
            elif action_type == 'lateral_movement':
                if not self.compromised_hosts:
                    result['details'] = 'No hosts compromised yet for lateral movement.'
                    return result
                self.compromised_hosts.add(target)
                
            result['success'] = True
            result['logs_generated'] = new_logs
            result['details'] = f'Successfully executed {action_type} using {technique_id} on {target}.'
            
            self.action_history.append({'action': action, 'result': result})
            self.rounds_active += 1
            return result
            
        except Exception as e:
            logger.error(f"Agent {self.agent_id} execution failed: {e}")
            result['details'] = str(e)
            return result

    def receive_message(self, sender_id: str, message: str) -> None:
        self.discovered_info[f"msg_from_{sender_id}_{self.rounds_active}"] = message

    def send_message(self, recipient_id: str, message: str, comm_channel: AttackerCommChannel) -> None:
        comm_channel.send(self.agent_id, recipient_id, message)

    def observe_detection(self, was_detected: bool, details: dict) -> None:
        self.is_detected = was_detected
        if was_detected:
            stealth = self.personality_traits.get('stealth', 0.5)
            if stealth > 0.7:
                self.current_phase = 'dormant'
            elif self.personality_traits.get('aggression', 0.5) > 0.7:
                self.current_phase = 'exploitation'

    def get_status(self) -> dict:
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'phase': self.current_phase,
            'compromised_hosts': list(self.compromised_hosts),
            'detected': self.is_detected,
            'rounds_active': self.rounds_active
        }
