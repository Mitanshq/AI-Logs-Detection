from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os
import re
from datetime import datetime

app = Flask(__name__)

LOG_DIR = "test_logs"
os.makedirs(LOG_DIR, exist_ok=True)

DB_FILE = 'Servers/database_log.db'
USERS_FILE = 'Servers/database_users.db'
ANAMOLIES_FILES = 'Servers/database_anamolies.db'
CATEGORY_FILE = 'Servers/database_category.db'
REPORT_FILE = 'Servers/database_report.db'
PROCESSED_FILES = set()

# logs ============================================================================================================================================
def init_anamoliesLog():
    with sqlite3.connect(ANAMOLIES_FILES) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anamoliesLogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                timestamp TEXT, 
                IP TEXT,
                Filename TEXT,
                content TEXT, 
                Confidence REAL,
                Label INTEGER,
                FOREIGN KEY (Label) REFERENCES CATEGORY(Cat_ID)
            )
        """)
        conn.commit()
        
init_anamoliesLog()

def init_dbLogs():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                timestamp TEXT, 
                IP TEXT,
                Filename TEXT,
                content TEXT, 
                Label INTEGER,
                FOREIGN KEY (Label) REFERENCES CATEGORY(Cat_ID)
            )
        """)
        conn.commit()
        
init_dbLogs()

def process_logs():
    from prediction_model import predict_log
    global PROCESSED_FILES
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        for filename in os.listdir(LOG_DIR):
            if filename in PROCESSED_FILES:
                continue
            file_path = os.path.join(LOG_DIR, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as f:
                    for log in f:
                        log = log.strip()
                        classification, confidence = predict_log(log)
                        ip_address = extract_ip(log)
                        cleaned_log = remove_ip(log)
                        label = detect_label(filename)
                        if classification == 'Scam Log':
                            with sqlite3.connect(ANAMOLIES_FILES) as a_conn:
                                a_cursor = a_conn.cursor()
                                a_cursor.execute("""
                                    SELECT COUNT(*) FROM anamoliesLogs WHERE TRIM(content) = TRIM(?)
                                """, (cleaned_log,))
                                if a_cursor.fetchone()[0] == 0:
                                    a_cursor.execute("""
                                        INSERT INTO anamoliesLogs(timestamp, IP, Filename, content, Confidence, Label)
                                        VALUES(?, ?, ?, ?, ?, ?)
                                    """, (datetime.datetime.now().isoformat(), ip_address, filename, cleaned_log, confidence, get_category_id(label)))
                                    a_conn.commit()

                        cursor.execute("""
                            SELECT COUNT(*) FROM logs WHERE TRIM(content) = TRIM(?)
                        """, (cleaned_log,))
                        if cursor.fetchone()[0] == 0:
                            cursor.execute("""
                                INSERT INTO logs(timestamp, IP, Filename, content, Label)
                                VALUES(?, ?, ?, ?, ?)
                            """, (datetime.datetime.now().isoformat(), ip_address, filename, cleaned_log, get_category_id(label)))
                PROCESSED_FILES.add(filename)
        conn.commit()
        
def process_log_file(filename):
    from prediction_model import predict_log
    file_path = os.path.join(LOG_DIR, filename)
    if not os.path.isfile(file_path):
        return

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        with open(file_path, 'r') as f:
            for log in f:
                log = log.strip()
                classification, confidence = predict_log(log)
                ip_address = extract_ip(log)
                cleaned_log = remove_ip(log)
                label = detect_label(filename)
                if classification == 'Scam Log':
                    with sqlite3.connect(ANAMOLIES_FILES) as a_conn:
                        a_cursor = a_conn.cursor()
                        a_cursor.execute("""
                            SELECT COUNT(*) FROM anamoliesLogs WHERE TRIM(content) = TRIM(?)
                        """, (cleaned_log,))
                        if a_cursor.fetchone()[0] == 0:
                            a_cursor.execute("""
                                INSERT INTO anamoliesLogs(timestamp, IP, Filename, content, Confidence, Label)
                                VALUES(?, ?, ?, ?, ?, ?)
                            """, (datetime.datetime.now().isoformat(), ip_address, filename, cleaned_log, confidence, get_category_id(label)))
                            a_conn.commit()

                cursor.execute("""
                    SELECT COUNT(*) FROM logs WHERE TRIM(content) = TRIM(?)
                """, (cleaned_log,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO logs(timestamp, IP, Filename, content, Label)
                        VALUES(?, ?, ?, ?, ?)
                    """, (datetime.datetime.now().isoformat(), ip_address, filename, cleaned_log, get_category_id(label)))
                    
        conn.commit()
        
# =======================================================================================================================================================================

# Category Table
# ======================================================================================================================================================================
def init_category():
    with sqlite3.connect(CATEGORY_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS CATEGORY(
                           Cat_ID INTEGER PRIMARY KEY,
                           Category TEXT
                       )
                       """)
        
        conn.commit()
        
init_category()

def category():
    with sqlite3.connect(CATEGORY_FILE) as conn:
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT OR IGNORE INTO CATEGORY (Cat_ID, Category) VALUES (?, ?)
        """, [
            (101, "App Log"),
            (102, "Firewall Log"),
            (103, "Network Log"),
            (104, "Web Log"),
            (404, "Unknown")
        ])
        conn.commit()
        
category()
# =======================================================================================================================================================================

# reports ===================================================================================================================================================================

def init_reportDB():
    with sqlite3.connect(REPORT_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS REPORTS(
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            UserID INTEGER DEFAULT NULL,
                            LOG_ID INTEGER DEFAULT 404,
                            REPORT_TXT TEXT NOT NULL,
                            REPORTED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (UserID) REFERENCES USERS(ID),
                            FOREIGN KEY (LOG_ID) REFERENCES LOGS(ID)
                       )
                       """)
        conn.commit()
        
init_reportDB()
def process_reports():
    pass

# ============================================================================================================================================================================

# storing users ===========================================================================================================================================================

user_list = [1, 'Mitansh', 'mitanshcr7@gmail.com', '123456', 'admin']

def init_usersDB():
    with sqlite3.connect(USERS_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS USERS(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            USERNAME TEXT,
                            EMAIL TEXT,
                            PASSWORD TEXT,
                            role TEXT CHECK(role IN ('admin', 'analyst', 'viewer')) DEFAULT 'viewer',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
        
        conn.commit()
        
init_usersDB()
        
def store_users(users):
    with sqlite3.connect(USERS_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                        INSERT INTO USERS(id, USERNAME, EMAIL, PASSWORD, role)
                        VALUES(?, ?, ?, ?, ?)
                    """, (users[0], users[1], users[2], users[3], users[4]))
        conn.commit()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Funtions-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def remove_ip(log):
    ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    return re.sub(ip_pattern, "", log).strip()

def extract_ip(log):
    ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    ip_list = re.findall(ip_pattern, log)
    return ip_list[0] if ip_list else "Unknown"

def detect_related_logs(cursor, log_content, ip_address):
    cursor.execute("""
        SELECT id, content FROM logs WHERE IP = ? ORDER BY id DESC LIMIT 5
    """, (ip_address,))
    previous_logs = cursor.fetchall()
    related_logs = [log_id for log_id, content in previous_logs if log_content in content or content in log_content]
    if related_logs:
        print(f"Related logs found for new entry: {related_logs}")
        
def detect_label(file):
    if 'app' in file:
        return 'App Log'
    elif 'firewall' in file:
        return 'Firewall Log'
    elif 'network' in file:
        return 'Network Log'
    elif 'web' in file:
        return 'Web Log'
    else:
        return 'Unknown'
    
def get_category_id(label):
    with sqlite3.connect(CATEGORY_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Cat_ID FROM CATEGORY WHERE Category = ?", (label,))
        result = cursor.fetchone()
        return result[0] if result else 404

# -=========================================================================================================================================================================================
        

# Routes
# ===========================================================================================================================================================================================
@app.route("/upload_user", methods=['POST'])
def upload_users():
    store_users(user_list)
    return jsonify({"message": "User uploaded."})

@app.route("/upload_log", methods=['POST'])
def upload_log():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    filename = os.path.join(LOG_DIR, file.filename)
    file.save(filename)
    process_log_file(file.filename)
    return jsonify({"message": "Log file uploaded and processed."})

@app.route("/recieve_logs", methods=["GET"])
def recieve_logs():
    from prediction_model import predict_log
    data = request.json
    device = data.get("device")
    log_text = data.get("log")
    status = predict_log(log_text)
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.route("/logs", methods=["GET"])
def get_logs():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, IP, Filename, content, Label FROM logs")
        logs = cursor.fetchall()
    return jsonify([
        {"id": log[0], "timestamp": log[1], "IP": log[2], "Filename": log[3], "content": log[4], "Confidence": log[5], "Label": log[6]} 
        for log in logs
    ])

@app.route("/detect", methods=["POST"])
def detect_logs():
    from prediction_model import predict_log
    data = request.json
    if not data or "log_content" not in data:
        return jsonify({"error": "Invalid request"}), 400
    classification, confidence = predict_log(data["log_content"].strip())
    return jsonify({"classification": classification, "Confidence": confidence})

# ===============================================================================================================================================================================================

def run_flask():
    app.run(debug=False, port=5001, use_reloader=False)

if __name__ == "__main__":
    import threading
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    import time
    time.sleep(2)
    from log_monitor import start_monitoring
    start_monitoring()