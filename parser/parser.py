#!/usr/bin/env python3
"""
parser.py
Tail a hostapd/syslog file and extract failed WPA/WPA2 auth events.
Store results in SQLite and append to a CSV.

Usage:
  python3 parser.py --file /var/log/hostapd.log
"""

import re
import sqlite3
import csv
import argparse
import time
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DB_PATH = Path("data/attempts.db")
CSV_PATH = Path("data/attempts.csv")

# Patterns to tag common hostapd failure messages
LOG_KEYS = [
    (re.compile(r'WPA: 4-?Way Handshake failed', re.IGNORECASE), "4way-handshake-failed"),
    (re.compile(r'EAPOL pairwise key handshake failed', re.IGNORECASE), "eapol-handshake-failed"),
    (re.compile(r'authentication failed', re.IGNORECASE), "authentication-failed"),
    (re.compile(r'association denied', re.IGNORECASE), "association-denied"),
]

# Example hostapd line:
# Nov 12 15:32:10 hostname hostapd: wlan0: STA aa:bb:cc:dd:ee:ff WPA: 4-Way Handshake failed - ...
LINE_RE = re.compile(
    r'(?P<ts>\w+\s+\d+\s+\d+:\d+:\d+)\s+\S+\s+hostapd:\s+(?P<intf>\S+):\s+STA\s+(?P<mac>(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2})\s+(?P<msg>.+)',
    re.IGNORECASE
)

def ensure_db():
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
    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ts","device_mac","reason","raw"])

def parse_line(line):
    m = LINE_RE.search(line)
    if not m:
        return None
    ts_text = m.group("ts")
    # hostapd syslog usually lacks year; attach current year (acceptable for simple logging)
    try:
        ts = datetime.strptime(f"{ts_text} {datetime.now().year}", "%b %d %H:%M:%S %Y")
    except Exception:
        ts = datetime.now()
    mac = m.group("mac").lower()
    raw = m.group("msg").strip()
    for rx, reason in LOG_KEYS:
        if rx.search(raw):
            return {
                "ts": ts.isoformat(sep=' '),
                "mac": mac,
                "reason": reason,
                "raw": raw
            }
    return None

def store_item(item):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO attempts (ts, device_mac, reason, raw) VALUES (?, ?, ?, ?)",
              (item["ts"], item["mac"], item["reason"], item["raw"]))
    conn.commit()
    conn.close()
    with CSV_PATH.open("a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([item["ts"], item["mac"], item["reason"], item["raw"]])
    print(f"[{item['ts']}] {item['mac']} {item['reason']}")

class TailHandler(FileSystemEventHandler):
    def __init__(self, path):
        self.path = Path(path)
        self._fh = open(self.path, "r", errors="ignore")
        # seek to end by default
        self._fh.seek(0, 2)

    def on_modified(self, event):
        if event.src_path != str(self.path):
            return
        while True:
            line = self._fh.readline()
            if not line:
                break
            item = parse_line(line)
            if item:
                store_item(item)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="hostapd log file (e.g. /var/log/hostapd.log)")
    args = ap.parse_args()
    ensure_db()
    event_handler = TailHandler(args.file)
    observer = Observer()
    observer.schedule(event_handler, Path(args.file).parent, recursive=False)
    observer.start()
    print("Monitoring", args.file)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
