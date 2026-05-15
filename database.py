# database.py
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "tracker.db")

def get_db_connection():
    """Retorna una conexión activa a la base de datos SQLite."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa las tablas de la base de datos si no existen."""
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