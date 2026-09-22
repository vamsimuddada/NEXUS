import sqlite3
from typing import Dict, List
from pathlib import Path
from nexus.utils import get_logger

logger = get_logger(__name__)

class EloScoring:
    """Tracks AI vs AI performance using Elo ratings."""

    def __init__(self, db_path: str = "data/nexus_elo.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initializes the SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS elo_ratings (
                    agent_id TEXT PRIMARY KEY,
                    rating REAL DEFAULT 1000.0,
                    matches INTEGER DEFAULT 0
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS elo_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    rating REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def get_rating(self, agent_id: str) -> float:
        """Retrieves the current rating of an agent. Defaults to 1000.0."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT rating FROM elo_ratings WHERE agent_id = ?", (agent_id,))
            result = cursor.fetchone()
            return result[0] if result else 1000.0

    def _set_rating(self, agent_id: str, rating: float) -> None:
        """Sets and records a new rating for an agent."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO elo_ratings (agent_id, rating, matches)
                VALUES (?, ?, 1)
                ON CONFLICT(agent_id) DO UPDATE SET
                    rating = excluded.rating,
                    matches = matches + 1
            ''', (agent_id, rating))
            cursor.execute('''
                INSERT INTO elo_history (agent_id, rating)
                VALUES (?, ?)
            ''', (agent_id, rating))
            conn.commit()

    def update_ratings(self, attacker_id: str, defender_result: Dict) -> Dict:
        """
        Calculates and updates Elo ratings based on a match outcome.
        Attacker wins if not detected or blocked (defender_result indicates success).
        """
        k_factor = 32.0
        attacker_rating = self.get_rating(attacker_id)
        defender_id = defender_result.get("defender_id", "system")
        defender_rating = self.get_rating(defender_id)

        # Determine outcome: 1 if attacker won, 0 if defender won, 0.5 for draw
        detected = defender_result.get("detected", False)
        blocked = defender_result.get("blocked", False)
        
        if not detected and not blocked:
            attacker_score = 1.0
            defender_score = 0.0
        elif detected and not blocked:
            attacker_score = 0.5
            defender_score = 0.5
        else:
            attacker_score = 0.0
            defender_score = 1.0

        expected_attacker = 1.0 / (1.0 + 10.0 ** ((defender_rating - attacker_rating) / 400.0))
        expected_defender = 1.0 / (1.0 + 10.0 ** ((attacker_rating - defender_rating) / 400.0))

        new_attacker_rating = attacker_rating + k_factor * (attacker_score - expected_attacker)
        new_defender_rating = defender_rating + k_factor * (defender_score - expected_defender)

        self._set_rating(attacker_id, new_attacker_rating)
        self._set_rating(defender_id, new_defender_rating)

        logger.info(f"Updated Elo ratings: {attacker_id} -> {new_attacker_rating:.2f}, {defender_id} -> {new_defender_rating:.2f}")

        return {
            "attacker": {"id": attacker_id, "old_rating": attacker_rating, "new_rating": new_attacker_rating},
            "defender": {"id": defender_id, "old_rating": defender_rating, "new_rating": new_defender_rating}
        }

    def get_leaderboard(self) -> List[Dict]:
        """Returns a list of agents ordered by rating descending."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT agent_id, rating, matches FROM elo_ratings ORDER BY rating DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_rating_history(self, agent_id: str) -> List[Dict]:
        """Returns the rating history for a specific agent."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT rating, timestamp FROM elo_history WHERE agent_id = ? ORDER BY id ASC", (agent_id,))
            return [dict(row) for row in cursor.fetchall()]
