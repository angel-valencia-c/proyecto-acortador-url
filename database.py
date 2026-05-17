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
    """Inicializa las tablas con el schema completo."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            short_id   TEXT PRIMARY KEY,
            original_url TEXT NOT NULL,
            created_at DATETIME DEFAULT (datetime('now')),
            updated_at DATETIME DEFAULT (datetime('now')),
            is_active  INTEGER DEFAULT 1
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            short_id         TEXT,
            ip_address       TEXT,
            user_agent       TEXT,
            referer          TEXT,
            utm_source       TEXT,
            utm_medium       TEXT,
            utm_campaign     TEXT,
            utm_term         TEXT,
            utm_content      TEXT,
            gclid            TEXT,
            gbraid           TEXT,
            wbraid           TEXT,
            fbclid           TEXT,
            fb_action_ids    TEXT,
            fb_action_types  TEXT,
            ttclid           TEXT,
            msclkid          TEXT,
            twclid           TEXT,
            additional_params TEXT,
            device_type      TEXT,
            browser          TEXT,
            country          TEXT,
            timestamp        DATETIME,
            FOREIGN KEY(short_id) REFERENCES urls(short_id)
        )
    ''')

    conn.commit()
    conn.close()