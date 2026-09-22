from typing import Dict, Any

def move_laterally(digital_twin: Any, source_host: str, target_host: str, technique: str = 'T1021', **kwargs) -> Dict[str, Any]:
    path = digital_twin.network.path_exists(source_host, target_host)
    if not path:
        return {'success': False, 'results': 'No network path', 'logs_generated': []}
    logs = digital_twin.inject_attack_logs(technique, source_host, target_host, 'system')
    return {'success': True, 'results': f"Moved to {target_host}", 'logs_generated': logs}

def pass_the_hash(digital_twin: Any, source_host: str, target_host: str, credential_user: str, **kwargs) -> Dict[str, Any]:
    logs = digital_twin.inject_attack_logs('T1003', source_host, target_host, credential_user)
    return {'success': True, 'results': f"PTH successful to {target_host}", 'logs_generated': logs}

def remote_service_exploit(digital_twin: Any, source_host: str, target_host: str, **kwargs) -> Dict[str, Any]:
    logs = digital_twin.inject_attack_logs('T1021', source_host, target_host, 'system')
    return {'success': True, 'results': f"Exploited {target_host}", 'logs_generated': logs}
