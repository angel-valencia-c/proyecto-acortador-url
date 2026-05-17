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

    # --- Tabla urls: agregar columnas faltantes ---
    columnas_urls = [
        "ALTER TABLE urls ADD COLUMN created_at DATETIME DEFAULT (datetime('now'))",
        "ALTER TABLE urls ADD COLUMN updated_at DATETIME DEFAULT (datetime('now'))",
        "ALTER TABLE urls ADD COLUMN is_active INTEGER DEFAULT 1",
    ]

    # --- Tabla visits: agregar columnas faltantes ---
    columnas_visits = [
        "ALTER TABLE visits ADD COLUMN utm_term TEXT",
        "ALTER TABLE visits ADD COLUMN utm_content TEXT",
        "ALTER TABLE visits ADD COLUMN gclid TEXT",
        "ALTER TABLE visits ADD COLUMN fbclid TEXT",
        "ALTER TABLE visits ADD COLUMN ttclid TEXT",
        "ALTER TABLE visits ADD COLUMN msclkid TEXT",
        "ALTER TABLE visits ADD COLUMN additional_params TEXT",
        "ALTER TABLE visits ADD COLUMN device_type TEXT",
        "ALTER TABLE visits ADD COLUMN browser TEXT",
    ]

    for sql in columnas_urls + columnas_visits:
        try:
            cursor.execute(sql)
            col = sql.split("ADD COLUMN")[1].strip().split()[0]
            print(f"  ✅ Columna agregada: {col}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                col = sql.split("ADD COLUMN")[1].strip().split()[0]
                print(f"  ⏭️  Ya existe: {col}")
            else:
                print(f"  ❌ Error: {e}")

    conn.commit()
    conn.close()
    print("\n✅ Migración completada.")

if __name__ == "__main__":
    migrate()