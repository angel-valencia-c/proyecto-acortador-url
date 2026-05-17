# migrate.py
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv("DB_NAME", "tracker.db")

def migrate():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    print("🔄 Iniciando migración...")

    columnas = [
        ("urls", "created_at", "DATETIME DEFAULT (datetime('now'))"),
        ("urls", "updated_at", "DATETIME DEFAULT (datetime('now'))"),
        ("urls", "is_active",  "INTEGER DEFAULT 1"),
        ("visits", "utm_term",         "TEXT"),
        ("visits", "utm_content",      "TEXT"),
        ("visits", "gclid",            "TEXT"),
        ("visits", "gbraid",           "TEXT"),
        ("visits", "wbraid",           "TEXT"),
        ("visits", "fbclid",           "TEXT"),
        ("visits", "fb_action_ids",    "TEXT"),
        ("visits", "fb_action_types",  "TEXT"),
        ("visits", "ttclid",           "TEXT"),
        ("visits", "msclkid",          "TEXT"),
        ("visits", "twclid",           "TEXT"),
        ("visits", "additional_params","TEXT"),
        ("visits", "device_type",      "TEXT"),
        ("visits", "browser",          "TEXT"),
    ]

    for tabla, col, tipo in columnas:
        try:
            cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {col} {tipo}")
            print(f"  ✅ {tabla}.{col}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"  ⏭️  ya existe: {tabla}.{col}")
            else:
                print(f"  ❌ Error: {e}")

    conn.commit()
    conn.close()
    print("\n✅ Migración completada.")

if __name__ == "__main__":
    migrate()