from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class TechniqueInfo:
    technique_id: str
    name: str
    tactic: str
    description: str
    event_patterns: List[int]

class AttackLabeler:
    def __init__(self):
        self.techniques = {
            'T1078': TechniqueInfo('T1078', 'Valid Accounts', 'Defense Evasion', 'Adversaries may obtain and abuse credentials of existing accounts', []),
            'T1566': TechniqueInfo('T1566', 'Phishing', 'Initial Access', 'Adversaries may send phishing messages to gain access', []),
            'T1059': TechniqueInfo('T1059', 'Command and Scripting Interpreter', 'Execution', 'Adversaries may abuse command and script interpreters', [4688]),
            'T1053': TechniqueInfo('T1053', 'Scheduled Task/Job', 'Execution', 'Adversaries may abuse task scheduling functionality', []),
            'T1547': TechniqueInfo('T1547', 'Boot or Logon Autostart Execution', 'Persistence', 'Adversaries may achieve persistence by adding a program to a startup folder or registry run key', [4688]),
            'T1136': TechniqueInfo('T1136', 'Create Account', 'Persistence', 'Adversaries may create an account to maintain access', [4720, 4732]),
            'T1068': TechniqueInfo('T1068', 'Exploitation for Privilege Escalation', 'Privilege Escalation', 'Adversaries may exploit software vulnerabilities to elevate privileges', [4688]),
            'T1070': TechniqueInfo('T1070', 'Indicator Removal', 'Defense Evasion', 'Adversaries may delete or modify artifacts generated within systems to remove evidence', [1102]),
            'T1562': TechniqueInfo('T1562', 'Impair Defenses', 'Defense Evasion', 'Adversaries may maliciously modify components of a victim environment to hinder or disable defensive mechanisms', [4688]),
            'T1003': TechniqueInfo('T1003', 'OS Credential Dumping', 'Credential Access', 'Adversaries may attempt to dump credentials to obtain account login and credential material', [4688]),
            'T1110': TechniqueInfo('T1110', 'Brute Force', 'Credential Access', 'Adversaries may use brute force techniques to gain access to accounts', [4625]),
            'T1087': TechniqueInfo('T1087', 'Account Discovery', 'Discovery', 'Adversaries may attempt to get a listing of local system or domain accounts', []),
            'T1046': TechniqueInfo('T1046', 'Network Service Discovery', 'Discovery', 'Adversaries may attempt to get a listing of services listening on remote hosts', []),
            'T1021': TechniqueInfo('T1021', 'Remote Services', 'Lateral Movement', 'Adversaries may use Valid Accounts to log into a service specifically designed to accept remote connections', [4624]),
            'T1570': TechniqueInfo('T1570', 'Lateral Tool Transfer', 'Lateral Movement', 'Adversaries may transfer tools or other files between systems in a compromised environment', []),
            'T1005': TechniqueInfo('T1005', 'Data from Local System', 'Collection', 'Adversaries may search local system sources, such as file systems and configuration files or local databases, to find files of interest', []),
            'T1041': TechniqueInfo('T1041', 'Exfiltration Over C2 Channel', 'Exfiltration', 'Adversaries may steal data by exfiltrating it over an existing command and control channel', []),
            'T1048': TechniqueInfo('T1048', 'Exfiltration Over Alternative Protocol', 'Exfiltration', 'Adversaries may steal data by exfiltrating it over a different protocol than that of the existing command and control channel', []),
            'T1486': TechniqueInfo('T1486', 'Data Encrypted for Impact', 'Impact', 'Adversaries may encrypt data on target systems or on large numbers of systems in a network to interrupt availability to system and network resources', [4688]),
            'T1489': TechniqueInfo('T1489', 'Service Stop', 'Impact', 'Adversaries may stop or disable services on a system to render those services unavailable to legitimate users', [])
        }
        self.failed_logon_counts = {}

    def label_event(self, log_event: Dict) -> Optional[str]:
        if log_event.get('attack_technique_id'):
            return log_event['attack_technique_id']
            
        event_id = log_event.get('event_id')
        if event_id == 1102:
            return 'T1070'
        elif event_id in (4720, 4732):
            return 'T1136'
        elif event_id == 4625:
            user = log_event.get('user')
            if user:
                self.failed_logon_counts[user] = self.failed_logon_counts.get(user, 0) + 1
                if self.failed_logon_counts[user] > 3:
                    return 'T1110'
        return None

    def get_technique_info(self, technique_id: str) -> Optional[TechniqueInfo]:
        return self.techniques.get(technique_id)

    def get_ground_truth(self, logs: List[Dict]) -> List[Dict]:
        ground_truth = []
        for log in logs:
            label = self.label_event(log)
            if label:
                truth_entry = log.copy()
                truth_entry['attack_technique_id'] = label
                info = self.get_technique_info(label)
                if info:
                    truth_entry['technique_name'] = info.name
                    truth_entry['tactic'] = info.tactic
                ground_truth.append(truth_entry)
        return ground_truth
