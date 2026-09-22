"""
NEXUS Database Configuration.

Centralized manager for all database paths. Every component that needs
a database should get its path from here instead of hardcoding.
"""

import os
import sqlite3
from typing import Optional


class NexusDB:
    """
    Centralized database path manager.

    All SQLite databases are stored under a single base directory.
    Components request their specific database path from this class.

    Usage:
        db = NexusDB("data")
        gap_analyzer = GapAnalyzer(db_path=db.gaps)
        elo = EloScoring(db_path=db.elo)
    """

    def __init__(self, base_dir: str = "data") -> None:
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    @property
    def gaps(self) -> str:
        """Gap analysis results database."""
        return os.path.join(self.base_dir, "nexus_gaps.db")

    @property
    def training(self) -> str:
        """Model training history database."""
        return os.path.join(self.base_dir, "nexus_training.db")

    @property
    def elo(self) -> str:
        """ELO scoring database."""
        return os.path.join(self.base_dir, "nexus_elo.db")

    @property
    def replays(self) -> str:
        """Campaign replay database."""
        return os.path.join(self.base_dir, "nexus_replays.db")

    @property
    def results(self) -> str:
        """Simulation results database."""
        return os.path.join(self.base_dir, "nexus_results.db")

    @property
    def communications(self) -> str:
        """Attacker communication database."""
        return os.path.join(self.base_dir, "nexus_comms.db")

    @property
    def chromadb(self) -> str:
        """ChromaDB vector store directory."""
        path = os.path.join(self.base_dir, "chromadb")
        os.makedirs(path, exist_ok=True)
        return path

    def get_connection(self, db_path: str) -> sqlite3.Connection:
        """Get a SQLite connection with WAL mode for better concurrency."""
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn
