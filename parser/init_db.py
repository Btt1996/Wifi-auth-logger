#!/usr/bin/env python3
from pathlib import Path
import sqlite3

DB_PATH = Path("data/attempts.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        device_mac TEXT,
        reason TEXT,
        raw TEXT
    )
''')
conn.commit()
conn.close()
print("DB initialized at", DB_PATH)
