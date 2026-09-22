"""Automated response engine module."""
import datetime
from typing import List, Dict, Any
from nexus.utils import get_logger

logger = get_logger(__name__)

class AutomatedResponseEngine:
    """Executes automated SOAR responses."""

    def __init__(self):
        """Initialize engine."""
        self.action_logs: List[Dict] = []

    def _log_action(self, action: str, details: Dict) -> None:
        log_entry = {
            'action': action,
            'details': details,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.action_logs.append(log_entry)
        logger.info(f"ResponseEngine Action: {action} - {details}")

    def isolate_host(self, digital_twin: Any, host: str) -> None:
        """Isolate a host on the network."""
        if hasattr(digital_twin, 'isolate_network_host'):
            digital_twin.isolate_network_host(host)
            self._log_action('isolate_host', {'host': host})
        else:
            logger.error("digital_twin missing isolate_network_host")

    def disable_account(self, digital_twin: Any, username: str) -> None:
        """Disable a user account."""
        if hasattr(digital_twin, 'disable_user_account'):
            digital_twin.disable_user_account(username)
            self._log_action('disable_account', {'username': username})
        else:
            logger.error("digital_twin missing disable_user_account")

    def block_ip(self, digital_twin: Any, ip: str) -> None:
        """Block an IP address."""
        if hasattr(digital_twin, 'add_firewall_rule'):
            digital_twin.add_firewall_rule('block', ip)
            self._log_action('block_ip', {'ip': ip})
        else:
            logger.error("digital_twin missing add_firewall_rule")

    def quarantine_file(self, digital_twin: Any, host: str, file_path: str) -> None:
        """Quarantine a file."""
        if hasattr(digital_twin, 'remove_file'):
            digital_twin.remove_file(host, file_path)
            self._log_action('quarantine_file', {'host': host, 'file_path': file_path})
        else:
            logger.error("digital_twin missing remove_file")

    def recommend_response(self, alert: Dict) -> Dict:
        """Rule-based recommendations based on alert type."""
        alert_type = alert.get('type', '').lower()
        if 'ransomware' in alert_type:
            return {'action': 'isolate_host', 'target': alert.get('host', 'unknown')}
        elif 'brute' in alert_type or 'login' in alert_type:
            return {'action': 'disable_account', 'target': alert.get('user', 'unknown')}
        elif 'malware' in alert_type or 'virus' in alert_type:
            return {'action': 'quarantine_file', 'target': alert.get('file_path', 'unknown'), 'host': alert.get('host', 'unknown')}
        elif 'c2' in alert_type or 'beacon' in alert_type:
            return {'action': 'block_ip', 'target': alert.get('remote_ip', 'unknown')}
        else:
            return {'action': 'investigate', 'target': 'alert'}

    def execute_playbook(self, digital_twin: Any, playbook_name: str, context: Dict) -> Dict:
        """Execute predefined response playbooks."""
        results = {'playbook': playbook_name, 'status': 'executed', 'actions': []}
        
        if playbook_name == 'ransomware_containment':
            host = context.get('host')
            if host:
                self.isolate_host(digital_twin, host)
                results['actions'].append(f"Isolated {host}")
                
        elif playbook_name == 'insider_threat':
            user = context.get('user')
            if user:
                self.disable_account(digital_twin, user)
                results['actions'].append(f"Disabled account {user}")
                
        elif playbook_name == 'apt_response':
            host = context.get('host')
            ip = context.get('c2_ip')
            if host:
                self.isolate_host(digital_twin, host)
                results['actions'].append(f"Isolated {host}")
            if ip:
                self.block_ip(digital_twin, ip)
                results['actions'].append(f"Blocked IP {ip}")
                
        else:
            logger.warning(f"Unknown playbook: {playbook_name}")
            results['status'] = 'failed'
            
        return results

    def mitigate(self, detection_result: Dict, digital_twin: Any = None) -> Dict:
        """Main entry point to mitigate a detected threat."""
        # Map the detection result to a recommendation
        recommendation = self.recommend_response(detection_result)
        
        # If digital_twin is provided, execute the recommended action
        if digital_twin and recommendation.get('action'):
            action = recommendation['action']
            target = recommendation.get('target')
            
            try:
                if action == 'isolate_host' and target:
                    self.isolate_host(digital_twin, target)
                elif action == 'disable_account' and target:
                    self.disable_account(digital_twin, target)
                elif action == 'block_ip' and target:
                    self.block_ip(digital_twin, target)
                elif action == 'quarantine_file':
                    host = recommendation.get('host', 'unknown')
                    self.quarantine_file(digital_twin, host, target)
            except Exception as e:
                logger.error(f"Failed to execute mitigation action {action}: {e}")
                
        # Return the mitigation response for the logs
        return {
            'status': 'mitigated' if digital_twin else 'recommended',
            'action': recommendation.get('action'),
            'target': recommendation.get('target'),
            'timestamp': datetime.datetime.now().isoformat()
        }
