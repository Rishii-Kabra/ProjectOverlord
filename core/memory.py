import sqlite3
import json


class TaskMemory:
    def __init__(self, db_path="overlord_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                         CREATE TABLE IF NOT EXISTS logs
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             role
                             TEXT,
                             content
                             TEXT,
                             timestamp
                             DATETIME
                             DEFAULT
                             CURRENT_TIMESTAMP
                         )
                         ''')
            conn.commit()

    def add_event(self, role: str, text: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO logs (role, content) VALUES (?, ?)",
                (role, text)
            )
            conn.commit()

    # CHECK THIS NAME CAREFULLY:
    def get_history(self):
        """Retrieves history and formats it for Gemini's SDK."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT role, content FROM logs ORDER BY id ASC")
            rows = cursor.fetchall()

        # Return as the list of dicts the Orchestrator expects
        return [{"role": r, "parts": [{"text": c}]} for r, c in rows]

    def clear_memory(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM logs")
            conn.commit()

    def get_summarized_history(self):
        """
        Returns a pruned version of history to stay under quota limits.
        Always keeps the original user request and the most recent context.
        """
        history = self.get_history()

        # If history is short, just return it
        if len(history) <= 6:
            return history

        # If history is getting long, we 'compress' it
        # Keep the very first message (the goal) and the last 5 interactions
        pruned_history = [history[0]] + history[-5:]
        return pruned_history