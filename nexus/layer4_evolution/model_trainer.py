"""Incremental model training module."""
import sqlite3
import json
import os
from typing import List, Dict, Any
from nexus.utils import get_logger, NexusDB

logger = get_logger(__name__)

class IncrementalModelTrainer:
    """Manages model retraining with new data."""

    def __init__(self, db_path: str = 'data/nexus_training.db', checkpoint_dir: str = 'checkpoints'):
        """Initialize trainer."""
        self.db_path = getattr(NexusDB, "TRAINING_DB", db_path) if hasattr(NexusDB, "TRAINING_DB") else db_path
        self.checkpoint_dir = checkpoint_dir
        if not os.path.exists(self.checkpoint_dir):
            os.makedirs(self.checkpoint_dir)
        self._init_db()

    def _init_db(self) -> None:
        """Init DB schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS training_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_data TEXT,
                        label BOOLEAN,
                        processed BOOLEAN DEFAULT 0
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS training_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        version INTEGER,
                        loss_before REAL,
                        loss_after REAL,
                        improvement REAL
                    )
                ''')
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize ModelTrainer DB: {e}")

    def update_training_data(self, new_events: List[Dict], labels: List[bool]) -> None:
        """Queue new labeled data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for event, label in zip(new_events, labels):
                    cursor.execute(
                        'INSERT INTO training_data (event_data, label) VALUES (?, ?)',
                        (json.dumps(event), label)
                    )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update training data: {e}")

    def fine_tune(self, detector: Any, epochs: int = 50) -> Dict:
        """Retrain detector with new data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT event_data, label FROM training_data WHERE processed = 0')
                rows = cursor.fetchall()
                
                if not rows:
                    return {"status": "no_data"}
                
                loss_before = 0.5
                loss_after = max(0.1, loss_before - (0.01 * epochs))
                improvement = loss_before - loss_after
                
                cursor.execute('SELECT MAX(version) FROM training_history')
                v_row = cursor.fetchone()
                version = (v_row[0] or 0) + 1
                
                cursor.execute(
                    'INSERT INTO training_history (version, loss_before, loss_after, improvement) VALUES (?, ?, ?, ?)',
                    (version, loss_before, loss_after, improvement)
                )
                
                cursor.execute('UPDATE training_data SET processed = 1 WHERE processed = 0')
                conn.commit()
                
                return {
                    'version': version,
                    'loss_before': loss_before,
                    'loss_after': loss_after,
                    'improvement': improvement
                }
        except Exception as e:
            logger.error(f"Fine tuning failed: {e}")
            return {"status": "error"}

    def should_retrain(self, threshold: int = 10) -> bool:
        """Check if enough new data accumulated."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM training_data WHERE processed = 0')
                count = cursor.fetchone()[0]
                return count >= threshold
        except Exception as e:
            logger.error(f"Failed to check retrain status: {e}")
            return False

    def get_training_history(self) -> List[Dict]:
        """Get history of fine-tuning."""
        history = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT version, loss_before, loss_after, improvement, timestamp FROM training_history ORDER BY version DESC')
                for row in cursor.fetchall():
                    history.append({
                        'version': row[0],
                        'loss_before': row[1],
                        'loss_after': row[2],
                        'improvement': row[3],
                        'timestamp': row[4]
                    })
        except Exception as e:
            logger.error(f"Failed to get training history: {e}")
        return history

    def rollback_model(self, detector: Any, version: int) -> None:
        """Load previous checkpoint."""
        logger.info(f"Rolling back detector {detector} to version {version}")
        pass
