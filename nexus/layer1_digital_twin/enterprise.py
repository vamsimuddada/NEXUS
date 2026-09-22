from dataclasses import dataclass
from typing import List, Dict, Optional
from .active_directory import ActiveDirectorySimulator, ADUser
from .network_topology import NetworkTopologyGenerator, Host
from .log_generator import WindowsEventLogGenerator
from .attack_labels import AttackLabeler

@dataclass
class EnterpriseStatus:
    company_name: str
    num_employees: int
    num_hosts: int
    num_subnets: int
    is_generated: bool

class DigitalTwinEnterprise:
    def __init__(self, company_name: str = 'Nexus Corp', num_employees: int = 100, num_subnets: int = 5, seed: Optional[int] = None):
        self.company_name = company_name
        self.num_employees = num_employees
        self.num_subnets = num_subnets
        self.seed = seed
        self.is_generated = False
        
        self.ad = ActiveDirectorySimulator(seed=seed)
        self.network = NetworkTopologyGenerator(seed=seed)
        self.log_gen = WindowsEventLogGenerator(seed=seed)
        self.labeler = AttackLabeler()
        
        self.logs: List[Dict] = []
        self.blocked_ips: List[str] = []
        self.resources: List[Dict] = []
        self.quarantined_files: List[Dict] = []

    def generate(self) -> None:
        if self.is_generated:
            return
            
        self.ad.generate_users(self.num_employees)
        self.ad.generate_service_accounts()
        
        users = [u.username for u in self.ad.get_all_accounts()]
        self.network.generate_topology(self.num_employees, users)
        
        hosts = [h.hostname for h in self.network.get_hosts()]
        self.logs = self.log_gen.generate_normal_activity(self.num_employees * 2, hosts, users)
        
        self.is_generated = True

    def get_status(self) -> EnterpriseStatus:
        return EnterpriseStatus(
            company_name=self.company_name,
            num_employees=self.num_employees,
            num_hosts=len(self.network.get_hosts()),
            num_subnets=self.num_subnets,
            is_generated=self.is_generated
        )

    def get_hosts(self) -> List[Host]:
        return self.network.get_hosts()

    def get_host_by_name(self, hostname: str) -> Optional[Host]:
        return self.network.get_host_by_name(hostname)

    def get_users(self) -> List[ADUser]:
        return self.ad.get_all_accounts()

    def get_user_by_name(self, username: str) -> Optional[ADUser]:
        return self.ad.get_user_by_name(username)

    def inject_attack_logs(self, technique_id: str, source_host: str, target_host: str, user: str = 'SYSTEM') -> List[Dict]:
        attack_logs = self.log_gen.generate_attack_sequence(technique_id, source_host, target_host, user)
        self.logs.extend(attack_logs)
        return attack_logs

    def get_recent_events(self, n: int = 50) -> List[Dict]:
        return self.logs[-n:] if self.logs else []

    def query_logs(self, query: Dict) -> List[Dict]:
        results = []
        for log in self.logs:
            match = True
            for k, v in query.items():
                if log.get(k) != v:
                    match = False
                    break
            if match:
                results.append(log)
        return results

    def isolate_network_host(self, hostname: str) -> bool:
        return self.network.isolate_host(hostname)

    def disable_user_account(self, username: str) -> bool:
        return self.ad.disable_account(username)

    def add_firewall_rule(self, action: str, source_ip: str) -> Dict:
        rule = {'action': action, 'source_ip': source_ip}
        if action.lower() in ('block', 'deny'):
            self.blocked_ips.append(source_ip)
        return rule

    def register_resource(self, resource: Dict) -> None:
        self.resources.append(resource)

    def remove_file(self, host: str, path: str) -> Dict:
        removal = {'host': host, 'path': path, 'status': 'quarantined'}
        self.quarantined_files.append(removal)
        return removal

    def get_ground_truth(self) -> List[Dict]:
        return self.labeler.get_ground_truth(self.logs)
