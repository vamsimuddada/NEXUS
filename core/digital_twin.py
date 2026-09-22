"""
NEXUS — Layer 1: Digital Twin Environment
Simulates an enterprise: Active Directory, hosts, network topology, and log generation.
ARM64-safe: pure Python + Faker, no native binaries.
"""

from __future__ import annotations

import json
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional

from faker import Faker

fake = Faker()
random.seed(42)


# ── Domain Models ─────────────────────────────────────────────────────────────

@dataclass
class ADUser:
    """Active Directory user account."""
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    display_name: str = ""
    email: str = ""
    department: str = ""
    role: str = ""            # e.g. "IT Admin", "Finance", "HR"
    is_admin: bool = False
    host_id: str = ""         # primary workstation
    groups: list[str] = field(default_factory=list)
    password_hash: str = ""   # simulated hash (not real)

    def __post_init__(self):
        if not self.username:
            name = fake.name()
            self.display_name = name
            self.username = name.lower().replace(" ", ".") + str(random.randint(1, 99))
            self.email = f"{self.username}@corp.local"
            self.password_hash = fake.sha256()


@dataclass
class Host:
    """Represents an enterprise endpoint or server."""
    host_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hostname: str = ""
    ip: str = ""
    os: str = "Windows Server 2022"
    role: str = "workstation"   # workstation | dc | fileserver | webserver | db
    subnet: str = "10.0.1.0/24"
    is_domain_controller: bool = False
    services: list[str] = field(default_factory=list)
    vulnerabilities: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.hostname:
            prefix = {"dc": "DC", "fileserver": "FS", "webserver": "WEB",
                      "db": "DB", "workstation": "WS"}.get(self.role, "HOST")
            self.hostname = f"{prefix}-{random.randint(100, 999)}"
        if not self.ip:
            self.ip = fake.ipv4_private()


@dataclass
class NetworkEdge:
    """A connection between two hosts (for graph modeling)."""
    src: str   # host_id
    dst: str   # host_id
    port: int = 445
    protocol: str = "TCP"
    label: str = "internal"


# ── Digital Twin ──────────────────────────────────────────────────────────────

class DigitalTwin:
    """
    Simulated enterprise environment.
    Generates AD users, hosts, network topology and Windows-style event logs.
    """

    DEPARTMENTS = ["IT", "Finance", "HR", "Engineering", "Sales", "Legal", "Executive"]
    ROLES = {
        "IT":          ["Sysadmin", "Network Engineer", "Help Desk"],
        "Finance":     ["Accountant", "CFO", "Analyst"],
        "HR":          ["HR Manager", "Recruiter"],
        "Engineering": ["Developer", "DevOps", "QA"],
        "Sales":       ["Sales Rep", "Account Manager"],
        "Legal":       ["Counsel", "Paralegal"],
        "Executive":   ["CEO", "CTO", "COO"],
    }

    def __init__(self, num_users: int = 50, num_hosts: int = 20, seed: int = 42):
        random.seed(seed)
        Faker.seed(seed)
        self.num_users = num_users
        self.num_hosts = num_hosts
        self.users: list[ADUser] = []
        self.hosts: list[Host] = []
        self.edges: list[NetworkEdge] = []
        self.domain = "corp.local"
        self._build()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        self._create_hosts()
        self._create_users()
        self._create_topology()

    def _create_hosts(self):
        # Domain Controller (always 1)
        dc = Host(hostname="DC-001", ip="10.0.0.1", role="dc",
                  os="Windows Server 2022", is_domain_controller=True,
                  services=["LDAP", "Kerberos", "DNS", "SMB"],
                  subnet="10.0.0.0/24")
        self.hosts.append(dc)

        # Servers
        server_roles = ["fileserver", "webserver", "db"]
        for role in server_roles:
            h = Host(role=role,
                     os="Windows Server 2019",
                     services=self._services_for_role(role),
                     subnet="10.0.0.0/24")
            self.hosts.append(h)

        # Workstations
        for _ in range(self.num_hosts - len(self.hosts)):
            h = Host(role="workstation",
                     os=random.choice(["Windows 11", "Windows 10"]),
                     services=["SMB", "RDP"],
                     subnet="10.0.1.0/24")
            self.hosts.append(h)

    def _services_for_role(self, role: str) -> list[str]:
        return {
            "fileserver": ["SMB", "NFS", "DFS"],
            "webserver":  ["HTTP", "HTTPS", "IIS"],
            "db":         ["MSSQL", "SMB"],
        }.get(role, ["SMB"])

    def _create_users(self):
        # Force at least one IT admin
        admin = ADUser(department="IT", role="Sysadmin", is_admin=True,
                       groups=["Domain Admins", "IT Staff"])
        admin.host_id = self.hosts[0].host_id  # DC
        self.users.append(admin)

        for _ in range(self.num_users - 1):
            dept = random.choice(self.DEPARTMENTS)
            role = random.choice(self.ROLES[dept])
            is_admin = dept == "IT" and role == "Sysadmin"
            groups = [f"{dept} Staff"]
            if is_admin:
                groups.append("Domain Admins")
            workstation = random.choice(
                [h for h in self.hosts if h.role == "workstation"] or self.hosts
            )
            u = ADUser(department=dept, role=role, is_admin=is_admin,
                       groups=groups, host_id=workstation.host_id)
            self.users.append(u)

    def _create_topology(self):
        """Create network edges: all hosts connect to DC, random lateral edges."""
        dc_id = self.hosts[0].host_id
        for host in self.hosts[1:]:
            self.edges.append(NetworkEdge(src=host.host_id, dst=dc_id,
                                          port=389, protocol="TCP", label="ldap"))
        # Random lateral connections
        for _ in range(self.num_hosts * 2):
            a, b = random.sample(self.hosts, 2)
            port = random.choice([445, 3389, 22, 80, 443])
            self.edges.append(NetworkEdge(src=a.host_id, dst=b.host_id,
                                          port=port, label="lateral"))

    # ── Log Generation ────────────────────────────────────────────────────────

    def generate_normal_log(self) -> dict:
        """Generate a realistic benign Windows Event Log entry."""
        user = random.choice(self.users)
        host = next((h for h in self.hosts if h.host_id == user.host_id), self.hosts[-1])
        event_types = [
            (4624, "An account was successfully logged on"),
            (4634, "An account was logged off"),
            (4648, "A logon was attempted using explicit credentials"),
            (5156, "The Windows Filtering Platform permitted a connection"),
            (4663, "An attempt was made to access an object"),
        ]
        eid, msg = random.choice(event_types)
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_id": eid,
            "message": msg,
            "user": user.username,
            "host": host.hostname,
            "ip_src": host.ip,
            "ip_dst": random.choice(self.hosts).ip,
            "department": user.department,
            "is_admin": user.is_admin,
            "label": "benign",
            "attack_technique": None,
        }

    def generate_attack_log(self, technique_id: str, attacker_name: str,
                            user: Optional[ADUser] = None,
                            target_host: Optional[Host] = None) -> dict:
        """
        Generate a log entry tagged with a MITRE ATT&CK technique.
        This is what attacker agents call to produce simulated malicious activity.
        """
        if user is None:
            user = random.choice(self.users)
        if target_host is None:
            target_host = random.choice(self.hosts)

        technique_map = {
            "T1078": {"event_id": 4624, "message": "Valid account logon (possible credential abuse)"},
            "T1021": {"event_id": 4624, "message": "Remote interactive logon (lateral movement)"},
            "T1059": {"event_id": 4688, "message": "Process created: cmd.exe / powershell.exe"},
            "T1055": {"event_id": 10,   "message": "Process injection detected"},
            "T1083": {"event_id": 4663, "message": "File/directory enumeration"},
            "T1003": {"event_id": 4662, "message": "Credential dumping attempt (LSASS)"},
            "T1486": {"event_id": 4663, "message": "Mass file modification (possible ransomware)"},
            "T1071": {"event_id": 5156, "message": "Unusual outbound connection (C2 beacon)"},
        }
        info = technique_map.get(technique_id, {
            "event_id": 4625, "message": f"Unknown technique {technique_id}"
        })

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_id": info["event_id"],
            "message": info["message"],
            "user": user.username,
            "host": target_host.hostname,
            "ip_src": random.choice(self.hosts).ip,
            "ip_dst": target_host.ip,
            "department": user.department,
            "is_admin": user.is_admin,
            "label": "malicious",
            "attack_technique": technique_id,
            "attacker": attacker_name,
        }

    def generate_log_stream(self, n_normal: int = 100,
                            n_attack: int = 10,
                            techniques: Optional[list[str]] = None) -> list[dict]:
        """Generate a mixed stream of normal + attack logs."""
        if techniques is None:
            techniques = ["T1078", "T1021", "T1059"]
        logs = [self.generate_normal_log() for _ in range(n_normal)]
        for t in (techniques * (n_attack // len(techniques) + 1))[:n_attack]:
            logs.append(self.generate_attack_log(t, "UNKNOWN"))
        random.shuffle(logs)
        return logs

    # ── Serialization ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "users": [u.__dict__ for u in self.users],
            "hosts": [h.__dict__ for h in self.hosts],
            "edges": [e.__dict__ for e in self.edges],
        }

    def summary(self) -> str:
        dc_count = sum(1 for h in self.hosts if h.is_domain_controller)
        admin_count = sum(1 for u in self.users if u.is_admin)
        return (
            f"[DigitalTwin] domain={self.domain} | "
            f"users={len(self.users)} (admins={admin_count}) | "
            f"hosts={len(self.hosts)} (DCs={dc_count}) | "
            f"edges={len(self.edges)}"
        )
