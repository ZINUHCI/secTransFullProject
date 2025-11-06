# local_db.py
import sqlite3

# Ensure the database exists and the tables are created
def init_db(self):
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    # Table for storing messages (per user)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT NOT NULL,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            message TEXT,
            direction TEXT CHECK(direction IN ('sent', 'received')) NOT NULL,
            type TEXT CHECK(type IN ('text', 'file')) DEFAULT 'text',
            filename TEXT,
            filepath TEXT,  
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table for storing the logged-in user's data, JWT, and private key
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_session (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            jwt_token TEXT,
            private_key TEXT,  -- Store the user’s private key here
            logged_in BOOLEAN DEFAULT 0,
            last_login DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# Fetch the currently logged-in user (if any)
def get_logged_in_user(self):
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT username, jwt_token, private_key FROM user_session WHERE logged_in=1 LIMIT 1")
    user = cursor.fetchone()

    conn.close()
    print(user)
    return user  # returns (username, jwt_token, private_key) or None