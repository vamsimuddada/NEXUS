import sqlite3
import json
from typing import Dict, List
from pathlib import Path
from nexus.utils import get_logger

logger = get_logger(__name__)

class CampaignReplay:
    """Records and retrieves step-by-step actions of a simulation campaign."""

    def __init__(self, db_path: str = "data/nexus_replay.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initializes the SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS replays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sim_id TEXT,
                    round_num INTEGER,
                    event_data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def record_event(self, sim_id: str, round_num: int, event: Dict) -> None:
        """Records a single event to the replay database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO replays (sim_id, round_num, event_data)
                VALUES (?, ?, ?)
            ''', (sim_id, round_num, json.dumps(event)))
            conn.commit()
        logger.info(f"Recorded event for simulation {sim_id}, round {round_num}")

    def get_replay(self, sim_id: str) -> List[Dict]:
        """Retrieves all events for a given simulation in chronological order."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT round_num, event_data, timestamp FROM replays WHERE sim_id = ? ORDER BY round_num ASC, id ASC", (sim_id,))
            results = []
            for row in cursor.fetchall():
                event = json.loads(row[1])
                event['round_num'] = row[0]
                event['timestamp'] = row[2]
                results.append(event)
            return results

    def get_timeline(self, sim_id: str) -> List[Dict]:
        """Retrieves key events (attacks, detections, responses) for a simulation."""
        replay_events = self.get_replay(sim_id)
        key_events = []
        for event in replay_events:
            event_type = event.get('type', '')
            if event_type in ('attack', 'detection', 'response', 'mitigation'):
                key_events.append(event)
        return key_events

    def compare_simulations(self, sim_ids: List[str]) -> Dict:
        """Compares multiple simulations and returns comparative metrics."""
        comparison = {}
        for sim_id in sim_ids:
            events = self.get_replay(sim_id)
            attacks = sum(1 for e in events if e.get('type') == 'attack')
            detections = sum(1 for e in events if e.get('type') == 'detection')
            duration = len(set(e.get('round_num', 0) for e in events))
            comparison[sim_id] = {
                'total_events': len(events),
                'attacks': attacks,
                'detections': detections,
                'rounds': duration
            }
        return comparison
