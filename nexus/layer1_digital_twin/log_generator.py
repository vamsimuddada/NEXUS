import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class WindowsEventLogGenerator:
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.current_time = datetime.utcnow() - timedelta(days=7)

    def advance_time(self, seconds: int) -> None:
        self.current_time += timedelta(seconds=seconds)

    def generate_normal_activity(self, count: int, hosts: List[str], users: List[str]) -> List[Dict]:
        logs = []
        for _ in range(count):
            self.advance_time(random.randint(1, 60))
            event_type = random.choices(
                ['logon', 'failed_logon', 'process_creation'],
                weights=[0.80, 0.05, 0.15]
            )[0]
            
            host = random.choice(hosts) if hosts else "unknown_host"
            user = random.choice(users) if users else "unknown_user"
            
            log = {
                'log_id': str(uuid.uuid4()),
                'timestamp': self.current_time.isoformat(),
                'source_host': host,
                'target_host': host,
                'user': user,
                'attack_technique_id': None
            }
            
            if event_type == 'logon':
                log['event_id'] = 4624
                log['details'] = 'Successful logon'
            elif event_type == 'failed_logon':
                log['event_id'] = 4625
                log['details'] = 'Failed logon attempt'
            elif event_type == 'process_creation':
                log['event_id'] = 4688
                process = random.choice(['explorer.exe', 'chrome.exe', 'winword.exe', 'outlook.exe'])
                log['details'] = f'Process created: {process}'
                
            logs.append(log)
        return logs

    def generate_attack_sequence(self, technique_id: str, attacker_host: str, target_host: str, user: str = 'SYSTEM') -> List[Dict]:
        logs = []
        base_log = {
            'source_host': attacker_host,
            'target_host': target_host,
            'user': user,
            'attack_technique_id': technique_id
        }
        
        def add_log(event_id: int, details: str, time_offset: int = 1):
            self.advance_time(time_offset)
            log = base_log.copy()
            log['log_id'] = str(uuid.uuid4())
            log['timestamp'] = self.current_time.isoformat()
            log['event_id'] = event_id
            log['details'] = details
            logs.append(log)

        if technique_id == 'T1110':
            for _ in range(5):
                add_log(4625, 'Failed logon attempt via brute force')
            add_log(4624, 'Successful logon after brute force')
        elif technique_id == 'T1136':
            add_log(4720, 'User account created')
            add_log(4732, 'User added to privileged group')
        elif technique_id == 'T1070':
            add_log(1102, 'Audit log cleared')
        elif technique_id == 'T1059':
            add_log(4688, 'Process created: powershell.exe -enc')
        elif technique_id == 'T1068':
            add_log(4688, 'Process created: exploit.exe')
        elif technique_id == 'T1547':
            add_log(4688, 'Process created: reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run')
        elif technique_id == 'T1003':
            add_log(4688, 'Process created: mimikatz.exe')
        elif technique_id == 'T1021':
            add_log(4624, 'Remote logon successful (Type 10)')
        elif technique_id == 'T1486':
            add_log(4688, 'Process created: encrypt.exe')
        elif technique_id == 'T1562':
            add_log(4688, 'Process created: disable_defender.exe')
        else:
            add_log(4688, 'Suspicious process creation')
            
        return logs
