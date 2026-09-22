import networkx as nx
import random
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Host:
    hostname: str
    ip_address: str
    subnet: str
    role: str
    os_type: str
    assigned_user: Optional[str] = None

class NetworkTopologyGenerator:
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.subnets = {
            'DMZ': '10.0.1.0/24',
            'Corporate': '10.0.2.0/24',
            'Server': '10.0.3.0/24',
            'Management': '10.0.4.0/24',
            'Guest': '10.0.5.0/24'
        }
        self.graph = nx.Graph()
        self.hosts: dict[str, Host] = {}

    def generate_topology(self, num_workstations: int, users: List[str]) -> nx.Graph:
        # Create firewalls
        fw_dmz = Host('fw-dmz-01', '10.0.1.1', 'DMZ', 'firewall', 'linux')
        fw_corp = Host('fw-corp-01', '10.0.2.1', 'Corporate', 'firewall', 'linux')
        fw_server = Host('fw-server-01', '10.0.3.1', 'Server', 'firewall', 'linux')
        
        self._add_host(fw_dmz)
        self._add_host(fw_corp)
        self._add_host(fw_server)
        
        # Connect firewalls (core)
        self.graph.add_edge('fw-dmz-01', 'fw-corp-01')
        self.graph.add_edge('fw-corp-01', 'fw-server-01')

        # Create servers
        servers = [
            Host('dc-01', '10.0.3.10', 'Server', 'server', 'windows'),
            Host('dc-02', '10.0.3.11', 'Server', 'server', 'windows'),
            Host('web-01', '10.0.1.10', 'DMZ', 'server', 'linux'),
            Host('db-01', '10.0.3.20', 'Server', 'server', 'linux')
        ]
        
        for server in servers:
            self._add_host(server)
            if server.subnet == 'DMZ':
                self.graph.add_edge(server.hostname, 'fw-dmz-01')
            else:
                self.graph.add_edge(server.hostname, 'fw-server-01')

        # Create workstations
        for i in range(num_workstations):
            hostname = f"ws-{i+1:03d}"
            ip = f"10.0.2.{i+10}"
            assigned_user = random.choice(users) if users else None
            ws = Host(hostname, ip, 'Corporate', 'workstation', 'windows', assigned_user)
            self._add_host(ws)
            self.graph.add_edge(hostname, 'fw-corp-01')
            
        return self.graph

    def _add_host(self, host: Host):
        self.hosts[host.hostname] = host
        self.graph.add_node(host.hostname, **host.__dict__)

    def get_hosts(self) -> List[Host]:
        return list(self.hosts.values())

    def get_host_by_name(self, hostname: str) -> Optional[Host]:
        return self.hosts.get(hostname)

    def path_exists(self, source: str, target: str) -> bool:
        if source in self.graph and target in self.graph:
            return nx.has_path(self.graph, source, target)
        return False

    def isolate_host(self, hostname: str) -> bool:
        if hostname in self.graph:
            edges = list(self.graph.edges(hostname))
            self.graph.remove_edges_from(edges)
            return True
        return False

    def get_subnet_hosts(self, subnet_name: str) -> List[Host]:
        return [host for host in self.hosts.values() if host.subnet == subnet_name]
