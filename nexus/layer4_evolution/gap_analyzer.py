"""Gap analysis module."""
import sqlite3
import json
from typing import List, Dict, Any
from nexus.utils import get_logger, NexusDB

logger = get_logger(__name__)

class GapAnalyzer:
    """Analyzes what the defender missed during a simulation."""

    def __init__(self, db_path: str = 'data/nexus_gaps.db'):
        """Initialize GapAnalyzer with SQLite DB."""
        self.db_path = getattr(NexusDB, "GAPS_DB", db_path) if hasattr(NexusDB, "GAPS_DB") else db_path
        self._init_db()

    def _init_db(self) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS gap_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sim_id TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        metrics TEXT,
                        missed_attacks TEXT,
                        false_alarms TEXT
                    )
                ''')
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize GapAnalyzer DB: {e}")

    def analyze(self, ground_truth: List[Dict], detections: List[Dict]) -> Dict:
        """Compute metrics, false negatives, and false positives."""
        gt_ids = {item.get('log_id') for item in ground_truth if 'log_id' in item}
        det_ids = {item.get('log_id') for item in detections if 'log_id' in item}

        true_positives = len(gt_ids.intersection(det_ids))
        false_negatives = len(gt_ids - det_ids)
        false_positives = len(det_ids - gt_ids)
        true_negatives = 0

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        missed_attacks = [item for item in ground_truth if item.get('log_id') not in det_ids]
        false_alarms = [item for item in detections if item.get('log_id') not in gt_ids]

        remediation = "Tune rules to reduce FP." if false_positives > false_negatives else "Add new rules for missed attacks."

        return {
            'metrics': {
                'TP': true_positives,
                'FP': false_positives,
                'FN': false_negatives,
                'TN': true_negatives,
                'precision': precision,
                'recall': recall,
                'f1': f1
            },
            'missed_attacks': missed_attacks,
            'false_alarms': false_alarms,
            'remediation': remediation
        }

    def track_improvement(self, sim_id: str, results: Dict) -> None:
        """Save results to track improvement over time."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO gap_analysis (sim_id, metrics, missed_attacks, false_alarms) VALUES (?, ?, ?, ?)',
                    (sim_id, json.dumps(results.get('metrics', {})), json.dumps(results.get('missed_attacks', [])), json.dumps(results.get('false_alarms', [])))
                )
                conn.commit()
                logger.info(f"Saved gap analysis for sim {sim_id}")
        except Exception as e:
            logger.error(f"Failed to track improvement: {e}")

    def get_improvement_trend(self) -> List[Dict]:
        """Get the trend of metrics over time."""
        trends = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT sim_id, timestamp, metrics FROM gap_analysis ORDER BY timestamp ASC')
                rows = cursor.fetchall()
                for row in rows:
                    trends.append({
                        'sim_id': row[0],
                        'timestamp': row[1],
                        'metrics': json.loads(row[2])
                    })
        except Exception as e:
            logger.error(f"Failed to get improvement trend: {e}")
        return trends

    def identify_blind_spots(self) -> List[Dict]:
        """Identify techniques that are consistently missed."""
        missed = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT missed_attacks FROM gap_analysis')
                rows = cursor.fetchall()
                tech_counts = {}
                for row in rows:
                    attacks = json.loads(row[0])
                    for atk in attacks:
                        tech = atk.get('technique_id', 'unknown')
                        tech_counts[tech] = tech_counts.get(tech, 0) + 1
                
                for tech, count in tech_counts.items():
                    if count >= 3:
                        missed.append({'technique_id': tech, 'miss_count': count})
        except Exception as e:
            logger.error(f"Failed to identify blind spots: {e}")
        return missed
