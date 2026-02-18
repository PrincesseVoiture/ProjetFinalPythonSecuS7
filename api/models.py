import sqlite3
import secrets

DB_FILE = "database.db"

class Database():
    def __init__(self) -> None:
        self.init_db()

    def init_db(self) -> None:
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

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            token TEXT UNIQUE
        )
        """)

        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            token = secrets.token_hex(16)  
            cursor.execute(
                "INSERT INTO users (username, password, token) VALUES (?, ?, ?)",
                ("admin", "admin", token)
            )

        cursor.execute("SELECT * FROM users WHERE username = 'Berzylyss'")
        if not cursor.fetchone():
            token = secrets.token_hex(16)
            cursor.execute(
                "INSERT INTO users (username, password, token) VALUES (?, ?, ?)",
                ("Berzylyss", "123456", token)
            )

        conn.commit()
        conn.close()

    def run_query(self, query: str, params=(), fetch: bool = False):
        """Exécute une requête SQL et retourne éventuellement les résultats."""
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(query, params)
        
        result = cursor.fetchall() if fetch else None

        conn.commit()
        conn.close()

        return result