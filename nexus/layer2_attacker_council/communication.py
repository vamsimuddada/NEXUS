import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from nexus.utils import get_logger

logger = get_logger(__name__)

class AttackerCommChannel:
    """SQLite-backed message broker for attacker agents."""

    def __init__(self, db_path: str = ':memory:'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id TEXT,
                    recipient_id TEXT,
                    message TEXT,
                    msg_type TEXT,
                    timestamp DATETIME,
                    is_read BOOLEAN DEFAULT 0
                )
            ''')

    def send(self, sender_id: str, recipient_id: str, message: str, msg_type: str = 'intel') -> None:
        """Send a message to a specific agent."""
        try:
            with self.conn:
                self.conn.execute('''
                    INSERT INTO messages (sender_id, recipient_id, message, msg_type, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (sender_id, recipient_id, message, msg_type, datetime.now().isoformat()))
                logger.info(f"Message sent from {sender_id} to {recipient_id}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    def receive(self, agent_id: str) -> List[Dict]:
        """Get unread messages for an agent and mark them as read."""
        try:
            with self.conn:
                cursor = self.conn.execute('''
                    SELECT * FROM messages 
                    WHERE (recipient_id = ? OR recipient_id = 'BROADCAST') AND is_read = 0
                ''', (agent_id,))
                rows = cursor.fetchall()
                
                if rows:
                    ids = [row['id'] for row in rows if row['recipient_id'] == agent_id]
                    if ids:
                        placeholders = ','.join('?' * len(ids))
                        self.conn.execute(f'''
                            UPDATE messages SET is_read = 1 WHERE id IN ({placeholders})
                        ''', ids)
                
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error receiving messages for {agent_id}: {e}")
            return []

    def broadcast(self, sender_id: str, message: str, msg_type: str = 'intel') -> None:
        """Send a message to all agents."""
        self.send(sender_id, 'BROADCAST', message, msg_type)

    def get_conversation_history(self, agent1: str, agent2: str) -> List[Dict]:
        """Get conversation history between two agents."""
        try:
            with self.conn:
                cursor = self.conn.execute('''
                    SELECT * FROM messages 
                    WHERE (sender_id = ? AND recipient_id = ?) 
                       OR (sender_id = ? AND recipient_id = ?)
                    ORDER BY timestamp ASC
                ''', (agent1, agent2, agent2, agent1))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
