import sqlite3

DB_NAME = "tracker.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
   
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            short_id TEXT PRIMARY KEY,
            original_url TEXT NOT NULL
        )
    ''')
    
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_id TEXT,
            ip_address TEXT,
            user_agent TEXT,
            referer TEXT,
            
            -- Nuevos campos de Marketing (Requerimiento del PDF)
            utm_source TEXT,
            utm_medium TEXT,
            utm_campaign TEXT,
            country TEXT,
            
            timestamp DATETIME,
            FOREIGN KEY(short_id) REFERENCES urls(short_id)
        )
    ''')
    conn.commit()
    conn.close()
   