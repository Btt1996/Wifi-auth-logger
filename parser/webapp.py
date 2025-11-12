#!/usr/bin/env python3
"""
webapp.py
Small Flask UI to view the most recent failed auth attempts and export CSV.
Run with: python3 webapp.py
"""
from flask import Flask, render_template_string, make_response
import sqlite3
import csv
from io import StringIO
from pathlib import Path

DB = Path("data/attempts.db")

TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>WiFi Auth Attempts</title>
  <style>
    body { font-family: system-ui, Arial; max-width: 980px; margin: 24px;}
    table { border-collapse: collapse; width: 100%;}
    th, td { border: 1px solid #ddd; padding: 8px; font-size: 13px;}
    th { background: #f2f2f2; }
    tr:hover { background: #fafafa; }
    .meta { margin-bottom: 12px; }
  </style>
</head>
<body>
<h1>Failed Wi‑Fi auth attempts</h1>
<div class="meta">
  <a href="/export/csv">Download CSV</a> · Showing up to 500 most recent entries
</div>
<table>
<tr><th>ID</th><th>Timestamp</th><th>MAC</th><th>Reason</th><th>Raw</th></tr>
{% for r in rows %}
<tr>
<td>{{r[0]}}</td>
<td>{{r[1]}}</td>
<td>{{r[2]}}</td>
<td>{{r[3]}}</td>
<td>{{r[4]}}</td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

def query_all(limit=500):
    if not DB.exists():
        return []
    conn = sqlite3.connect(str(DB))
    c = conn.cursor()
    c.execute("SELECT id, ts, device_mac, reason, raw FROM attempts ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

app = Flask(__name__)

@app.route("/")
def index():
    rows = query_all()
    return render_template_string(TEMPLATE, rows=rows)

@app.route("/export/csv")
def export_csv():
    rows = query_all(limit=1000000)  # export all (bounded by DB size)
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["ts", "device_mac", "reason", "raw"])
    for r in rows:
        writer.writerow([r[1], r[2], r[3], r[4]])
    output = si.getvalue()
    resp = make_response(output)
    resp.headers["Content-Disposition"] = "attachment; filename=attempts.csv"
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
