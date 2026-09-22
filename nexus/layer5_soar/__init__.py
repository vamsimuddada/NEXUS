"""Layer 5 SOAR module."""
from .honeypot import AdaptiveHoneypot
from .response_engine import AutomatedResponseEngine
from .threat_hunter import ProactiveThreatHunter

__all__ = [
    'AdaptiveHoneypot',
    'AutomatedResponseEngine',
    'ProactiveThreatHunter'
]
