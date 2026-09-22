"""
NEXUS MITRE ATT&CK Loader.

Provides technique metadata, kill chain ordering, and tactic filtering.
Uses hardcoded data for the 20 most common techniques so it works
offline without downloading the full ATT&CK STIX dataset.
"""

from typing import Any, Dict, List, Optional


# Kill chain tactics in execution order
KILL_CHAIN_TACTICS: List[str] = [
    "reconnaissance",
    "resource-development",
    "initial-access",
    "execution",
    "persistence",
    "privilege-escalation",
    "defense-evasion",
    "credential-access",
    "discovery",
    "lateral-movement",
    "collection",
    "command-and-control",
    "exfiltration",
    "impact",
]

# 20 major ATT&CK techniques with full metadata
TECHNIQUES: Dict[str, Dict[str, Any]] = {
    "T1566": {
        "name": "Phishing",
        "tactic": "initial-access",
        "description": "Adversaries send phishing messages to gain access.",
        "platforms": ["Windows", "Linux", "macOS"],
        "data_sources": ["Email", "Network Traffic"],
        "detection_tips": "Monitor for suspicious email attachments and links.",
    },
    "T1190": {
        "name": "Exploit Public-Facing Application",
        "tactic": "initial-access",
        "description": "Exploit vulnerabilities in internet-facing systems.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Application Log", "Network Traffic"],
        "detection_tips": "Monitor web server logs for exploitation attempts.",
    },
    "T1059": {
        "name": "Command and Scripting Interpreter",
        "tactic": "execution",
        "description": "Abuse command and script interpreters to execute commands.",
        "platforms": ["Windows", "Linux", "macOS"],
        "data_sources": ["Process", "Command"],
        "detection_tips": "Monitor for encoded PowerShell, suspicious cmd usage.",
    },
    "T1053": {
        "name": "Scheduled Task/Job",
        "tactic": "persistence",
        "description": "Abuse task scheduling to execute malicious code.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Process", "Scheduled Job"],
        "detection_tips": "Monitor schtasks.exe and at.exe usage.",
    },
    "T1078": {
        "name": "Valid Accounts",
        "tactic": "initial-access",
        "description": "Use legitimate credentials to gain access.",
        "platforms": ["Windows", "Linux", "macOS"],
        "data_sources": ["Logon Session", "User Account"],
        "detection_tips": "Monitor for unusual logon patterns and times.",
    },
    "T1543": {
        "name": "Create or Modify System Process",
        "tactic": "persistence",
        "description": "Create or modify system-level processes for persistence.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Service", "Process"],
        "detection_tips": "Monitor new service installations.",
    },
    "T1547": {
        "name": "Boot or Logon Autostart Execution",
        "tactic": "persistence",
        "description": "Configure persistence via autostart mechanisms.",
        "platforms": ["Windows", "Linux", "macOS"],
        "data_sources": ["Windows Registry", "Process"],
        "detection_tips": "Monitor Run/RunOnce registry keys.",
    },
    "T1055": {
        "name": "Process Injection",
        "tactic": "defense-evasion",
        "description": "Inject code into processes to evade detection.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Process"],
        "detection_tips": "Monitor for unusual process memory access.",
    },
    "T1003": {
        "name": "OS Credential Dumping",
        "tactic": "credential-access",
        "description": "Dump credentials from the OS for lateral movement.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Process", "Command"],
        "detection_tips": "Monitor for mimikatz, lsass access.",
    },
    "T1110": {
        "name": "Brute Force",
        "tactic": "credential-access",
        "description": "Use brute-force techniques to obtain credentials.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Logon Session", "User Account"],
        "detection_tips": "Monitor for multiple failed logon attempts.",
    },
    "T1082": {
        "name": "System Information Discovery",
        "tactic": "discovery",
        "description": "Gather system information for planning further actions.",
        "platforms": ["Windows", "Linux", "macOS"],
        "data_sources": ["Process", "Command"],
        "detection_tips": "Monitor for systeminfo, hostname commands.",
    },
    "T1046": {
        "name": "Network Service Discovery",
        "tactic": "discovery",
        "description": "Scan for services running on remote hosts.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Network Traffic"],
        "detection_tips": "Monitor for port scanning activity.",
    },
    "T1049": {
        "name": "System Network Connections Discovery",
        "tactic": "discovery",
        "description": "Discover network connections on the system.",
        "platforms": ["Windows", "Linux", "macOS"],
        "data_sources": ["Process", "Command"],
        "detection_tips": "Monitor for netstat, ss usage.",
    },
    "T1021": {
        "name": "Remote Services",
        "tactic": "lateral-movement",
        "description": "Use remote services to move laterally in the network.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Logon Session", "Network Traffic"],
        "detection_tips": "Monitor RDP, SSH, SMB logon events.",
    },
    "T1090": {
        "name": "Proxy",
        "tactic": "command-and-control",
        "description": "Use a proxy to direct network traffic through an intermediary.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Network Traffic"],
        "detection_tips": "Monitor for unusual proxy configurations.",
    },
    "T1571": {
        "name": "Non-Standard Port",
        "tactic": "command-and-control",
        "description": "Use non-standard ports for C2 communication.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Network Traffic"],
        "detection_tips": "Monitor for traffic on unusual ports.",
    },
    "T1041": {
        "name": "Exfiltration Over C2 Channel",
        "tactic": "exfiltration",
        "description": "Exfiltrate data over the existing C2 channel.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Network Traffic"],
        "detection_tips": "Monitor for large outbound data transfers.",
    },
    "T1048": {
        "name": "Exfiltration Over Alternative Protocol",
        "tactic": "exfiltration",
        "description": "Exfiltrate data using a different protocol than C2.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Network Traffic"],
        "detection_tips": "Monitor DNS, ICMP for data exfiltration.",
    },
    "T1485": {
        "name": "Data Destruction",
        "tactic": "impact",
        "description": "Destroy data and files on target systems.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["File", "Process"],
        "detection_tips": "Monitor for mass file deletion.",
    },
    "T1486": {
        "name": "Data Encrypted for Impact",
        "tactic": "impact",
        "description": "Encrypt data on target systems (ransomware).",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["File", "Process"],
        "detection_tips": "Monitor for rapid file encryption patterns.",
    },
    "T1070": {
        "name": "Indicator Removal",
        "tactic": "defense-evasion",
        "description": "Delete or modify artifacts to hide activity.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Windows Event Log", "File"],
        "detection_tips": "Monitor for log clearing (Event ID 1102).",
    },
    "T1562": {
        "name": "Impair Defenses",
        "tactic": "defense-evasion",
        "description": "Disable or modify security tools.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Service", "Process"],
        "detection_tips": "Monitor for security tool termination.",
    },
    "T1136": {
        "name": "Create Account",
        "tactic": "persistence",
        "description": "Create new accounts for persistence.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["User Account"],
        "detection_tips": "Monitor for Event ID 4720 (account creation).",
    },
    "T1068": {
        "name": "Exploitation for Privilege Escalation",
        "tactic": "privilege-escalation",
        "description": "Exploit software vulnerabilities to gain elevated access.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Process"],
        "detection_tips": "Monitor for known exploit binaries.",
    },
    "T1087": {
        "name": "Account Discovery",
        "tactic": "discovery",
        "description": "Enumerate accounts on a system or domain.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Process", "Command"],
        "detection_tips": "Monitor for net user, net group commands.",
    },
    "T1005": {
        "name": "Data from Local System",
        "tactic": "collection",
        "description": "Collect data from the local system.",
        "platforms": ["Windows", "Linux", "macOS"],
        "data_sources": ["File", "Process"],
        "detection_tips": "Monitor for access to sensitive file paths.",
    },
    "T1036": {
        "name": "Masquerading",
        "tactic": "defense-evasion",
        "description": "Match the name or location of legitimate files.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["File", "Process"],
        "detection_tips": "Monitor for processes with legitimate names in wrong paths.",
    },
    "T1027": {
        "name": "Obfuscated Files or Information",
        "tactic": "defense-evasion",
        "description": "Use obfuscation to hide command content.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["File", "Process"],
        "detection_tips": "Monitor for base64 encoded content.",
    },
    "T1133": {
        "name": "External Remote Services",
        "tactic": "initial-access",
        "description": "Leverage external-facing remote services for access.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Logon Session"],
        "detection_tips": "Monitor for VPN/RDP access from unusual locations.",
    },
    "T1489": {
        "name": "Service Stop",
        "tactic": "impact",
        "description": "Stop services to disrupt availability.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Service", "Process"],
        "detection_tips": "Monitor for critical service termination.",
    },
    "T1491": {
        "name": "Defacement",
        "tactic": "impact",
        "description": "Modify visual content for messaging.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["File", "Application Log"],
        "detection_tips": "Monitor for web content modifications.",
    },
    "T1498": {
        "name": "Network Denial of Service",
        "tactic": "impact",
        "description": "Perform denial of service attacks.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Network Traffic"],
        "detection_tips": "Monitor for traffic volume spikes.",
    },
    "T1570": {
        "name": "Lateral Tool Transfer",
        "tactic": "lateral-movement",
        "description": "Transfer tools between systems in the network.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Network Traffic", "File"],
        "detection_tips": "Monitor for file transfers between internal hosts.",
    },
    "T1105": {
        "name": "Ingress Tool Transfer",
        "tactic": "command-and-control",
        "description": "Transfer tools from an external system into the network.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Network Traffic", "File"],
        "detection_tips": "Monitor for downloads of executables.",
    },
    "T1490": {
        "name": "Inhibit System Recovery",
        "tactic": "impact",
        "description": "Delete or disable system recovery features.",
        "platforms": ["Windows"],
        "data_sources": ["Process", "Command"],
        "detection_tips": "Monitor for vssadmin delete shadows.",
    },
}


class MitreAttackLoader:
    """
    MITRE ATT&CK technique metadata loader.

    Provides technique info, tactic filtering, and kill chain ordering.
    Works fully offline with hardcoded data for 30+ techniques.
    """

    def __init__(self) -> None:
        self.techniques = TECHNIQUES

    def get_technique(self, technique_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific technique by ID."""
        info = self.techniques.get(technique_id)
        if info:
            return {"technique_id": technique_id, **info}
        return None

    def get_techniques_by_tactic(self, tactic: str) -> List[Dict[str, Any]]:
        """Get all techniques belonging to a specific tactic."""
        results = []
        for tid, info in self.techniques.items():
            if info["tactic"] == tactic:
                results.append({"technique_id": tid, **info})
        return results

    def get_all_tactics(self) -> List[str]:
        """Get all kill chain tactics in order."""
        return KILL_CHAIN_TACTICS.copy()

    def get_kill_chain(self, technique_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Sort technique IDs into kill chain execution order.

        Args:
            technique_ids: List of ATT&CK technique IDs.

        Returns:
            Sorted list of technique metadata dicts.
        """
        techniques_with_info = []
        for tid in technique_ids:
            info = self.get_technique(tid)
            if info:
                tactic = info["tactic"]
                order = (
                    KILL_CHAIN_TACTICS.index(tactic)
                    if tactic in KILL_CHAIN_TACTICS
                    else 99
                )
                techniques_with_info.append((order, info))

        techniques_with_info.sort(key=lambda x: x[0])
        return [info for _, info in techniques_with_info]

    def get_technique_name(self, technique_id: str) -> str:
        """Get human-readable name for a technique ID."""
        info = self.techniques.get(technique_id)
        return info["name"] if info else technique_id
