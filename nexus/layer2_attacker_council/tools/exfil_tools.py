from typing import Dict, Any

def collect_local_data(digital_twin: Any, host: str, **kwargs) -> Dict[str, Any]:
    logs = digital_twin.inject_attack_logs('T1005', host, host, 'system')
    return {'success': True, 'results': 'Data collected', 'logs_generated': logs}

def exfiltrate_data(digital_twin: Any, host: str, data_size_mb: int = 10, method: str = 'c2', **kwargs) -> Dict[str, Any]:
    tech = 'T1041' if method == 'c2' else 'T1048'
    logs = digital_twin.inject_attack_logs(tech, host, 'external', 'system')
    return {'success': True, 'results': f"Exfiltrated {data_size_mb}MB via {method}", 'logs_generated': logs}

def stage_data(digital_twin: Any, host: str, data: str, **kwargs) -> Dict[str, Any]:
    logs = digital_twin.inject_attack_logs('T1074', host, host, 'system')
    return {'success': True, 'results': 'Data staged', 'logs_generated': logs}
