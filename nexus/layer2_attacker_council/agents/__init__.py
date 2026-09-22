from .viper import VIPERAgent
from .kraken import KRAKENAgent
from .ghost import GHOSTAgent
from .hydra import HYDRAAgent
from .nova import NOVAAgent
from .cipher import CIPHERAgent

AGENT_REGISTRY = {
    'VIPER': VIPERAgent,
    'KRAKEN': KRAKENAgent,
    'GHOST': GHOSTAgent,
    'HYDRA': HYDRAAgent,
    'NOVA': NOVAAgent,
    'CIPHER': CIPHERAgent
}
