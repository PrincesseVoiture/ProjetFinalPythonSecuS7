import sqlite3

DB_FILE = "database.db"

class Database():
    def __init__(self) -> None:
        self.init_db()

    def init_db(self)-> None:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            cpu REAL,
            ram REAL,
            last_seen TEXT,
            status TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            command TEXT,
            status TEXT DEFAULT 'pending',
            result TEXT
        )
        """)

        conn.commit()
        conn.close()

    def run_query(self, query: str, params =(), fetch: bool =False):
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
        else:
            result = None
        conn.commit()
        conn.close()
        return result
