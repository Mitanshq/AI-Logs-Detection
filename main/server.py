from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os
import re
from datetime import datetime
from prediction_model import predict_log
# from alert import send_alert

app  = Flask(__name__)
db = 'logs.db'

TEMPLATE = """
<!DOCTYPE html>
<html><head><title>Logs</title><meta http-equiv="refresh" content="5">
<style>
body { font-family: sans-serif; }
.safe { color: green; }
.malicious { color: red; font-weight: bold; }
</style></head><body>
<h2>📡 Logs from Devices</h2>
{% for log in logs %}
<div class="{{log.status}}">{{log.time}} | {{log.device}} → {{log.log}} → {{log.status.upper()}}</div>
{% endfor %}
</body></html>
"""

def init_db():
    with sqlite3.connect(db) as conn:
        conn.execute("""
                     CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device TEXT,
                    message TEXT,
                    timestamp TEXT,
                    status TEXT
                )
                     """)
        
        
def insert_logs(device, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = predict_log(message)
    
    with sqlite3.connect(db) as conn:
        conn.execute("""
                     "INSERT INTO logs (device, message, timestamp, status) VALUES (?, ?, ?, ?)",
                    (device, message, timestamp, status)
                     """)
        conn.commit()
        
    if status == "Scam Log":
        pass
    
@app.route('/log', methods=['POST'])
def receive_log():
    data = request.json
    insert_logs(data.get("device"), data.get("log"))
    return jsonify({"status": "ok"})

@app.route('/')
def dashboard():
    with sqlite3.connect(db) as conn:
        logs = conn.execute("SELECT device, message, timestamp, status FROM logs ORDER BY id DESC").fetchall()
    return render_template_string(TEMPLATE, logs=logs)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
    
