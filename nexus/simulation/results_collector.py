import sqlite3
import json
import uuid
from typing import Dict, List
from datetime import datetime

class ResultsCollector:
    """SQLite logger for the simulation engine."""
    
    def __init__(self, db_path: str = "data/simulation_results.db"):
        import os
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        """Initializes the SQLite database and creates the results table if it does not exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS simulation_results (
                id TEXT PRIMARY KEY,
                sim_id TEXT,
                round_num INTEGER,
                event_type TEXT,
                timestamp TEXT,
                data TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
    def record(self, sim_id: str, round_num: int, event_type: str, data: Dict):
        """Records an event in the simulation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        record_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        cursor.execute(
            'INSERT INTO simulation_results (id, sim_id, round_num, event_type, timestamp, data) VALUES (?, ?, ?, ?, ?, ?)',
            (record_id, sim_id, round_num, event_type, timestamp, json.dumps(data))
        )
        conn.commit()
        conn.close()
        
    def get_simulation_results(self, sim_id: str) -> List[Dict]:
        """Retrieves all recorded events for a given simulation ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, sim_id, round_num, event_type, timestamp, data FROM simulation_results WHERE sim_id = ? ORDER BY round_num ASC, timestamp ASC',
            (sim_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "sim_id": row["sim_id"],
                "round_num": row["round_num"],
                "event_type": row["event_type"],
                "timestamp": row["timestamp"],
                "data": json.loads(row["data"])
            })
        return results
        
    def get_aggregate_stats(self, sim_ids: List[str]) -> Dict:
        """Calculates aggregate statistics for multiple simulations."""
        if not sim_ids:
            return {"total_events": 0, "breakdown": {}}
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        placeholders = ','.join(['?'] * len(sim_ids))
        cursor.execute(
            f'SELECT event_type, COUNT(*) FROM simulation_results WHERE sim_id IN ({placeholders}) GROUP BY event_type',
            tuple(sim_ids)
        )
        rows = cursor.fetchall()
        conn.close()
        
        stats = {row[0]: row[1] for row in rows}
        return {"total_events": sum(stats.values()), "breakdown": stats}
        
    def export_results(self, sim_id: str, format: str = 'json') -> str:
        """Exports the simulation results to a specific format."""
        results = self.get_simulation_results(sim_id)
        if format.lower() == 'json':
            return json.dumps(results, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
