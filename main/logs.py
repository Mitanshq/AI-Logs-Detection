import random
import time
import os
from datetime import datetime

os.makedirs("logs", exist_ok=True)

# Random IP generator
def random_ip():
    return ".".join(str(random.randint(1, 255)) for _ in range(4))

# Random protocol
def random_protocol():
    return random.choice(["TCP", "UDP", "ICMP"])

# Random HTTP methods
def random_http_method():
    return random.choice(["GET", "POST", "PUT", "DELETE"])

# Random user agent
def random_user_agent():
    return random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Chrome/114.0.5735.199 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "curl/7.68.0"
    ])

# Random status codes
def random_status_code():
    return random.choice([200, 201, 403, 404, 500])

# Random firewall actions
def random_firewall_action():
    return random.choice(["ALLOW", "DENY", "BLOCK"])

# Random web attack types
def random_scam_reason():
    return random.choice([
        "Brute Force Attack",
        "SQL Injection",
        "Cross-Site Scripting (XSS)",
        "DDoS Attempt",
        "Phishing",
        "Unauthorized Access",
        "Malware Injection"
    ])

# Generate genuine firewall log
def generate_genuine_firewall_log():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    src_ip, dst_ip = random_ip(), random_ip()
    protocol, action = random_protocol(), "ALLOW"
    return f"[{timestamp}] SRC={src_ip} DST={dst_ip} PROTO={protocol} ACTION={action}"

# Generate scam firewall log
def generate_scam_firewall_log():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    src_ip, dst_ip = random_ip(), random_ip()
    protocol, action, scam_reason = random_protocol(), "BLOCK", random_scam_reason()
    return f"[{timestamp}] SCAM ALERT: {scam_reason} SRC={src_ip} DST={dst_ip} PROTO={protocol} ACTION={action}"

# Generate genuine network log
def generate_genuine_network_log():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    src_ip, dst_ip, protocol = random_ip(), random_ip(), random_protocol()
    return f"[{timestamp}] NETWORK TRAFFIC SRC={src_ip} DST={dst_ip} PROTOCOL={protocol} STATUS=OK"

# Generate scam network log
def generate_scam_network_log():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    src_ip, dst_ip, protocol, scam_reason = random_ip(), random_ip(), random_protocol(), random_scam_reason()
    return f"[{timestamp}] NETWORK ALERT: {scam_reason} SRC={src_ip} DST={dst_ip} PROTOCOL={protocol} STATUS=SUSPICIOUS"

# Generate genuine web log
def generate_genuine_web_log():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip, method, status, user_agent = random_ip(), random_http_method(), random_status_code(), random_user_agent()
    return f"[{timestamp}] WEB REQUEST IP={ip} METHOD={method} STATUS={status} USER_AGENT={user_agent}"

# Generate scam web log
def generate_scam_web_log():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip, method, scam_reason, user_agent = random_ip(), random_http_method(), random_scam_reason(), random_user_agent()
    return f"[{timestamp}] WEB ALERT: {scam_reason} IP={ip} METHOD={method} STATUS=403 USER_AGENT={user_agent}"

# Generate genuine app log
def generate_genuine_app_log():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id, action = random.randint(1000, 9999), random.choice(["Login", "Logout", "Viewed Profile", "Updated Settings"])
    return f"[{timestamp}] APP ACTIVITY USER_ID={user_id} ACTION={action} STATUS=SUCCESS"

# Generate scam app log
def generate_scam_app_log():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id, scam_reason = random.randint(1000, 9999), random_scam_reason()
    return f"[{timestamp}] APP ALERT: {scam_reason} USER_ID={user_id} STATUS=FAILED"

# Write logs to files
def generate_logs(log_count=100000, delay=1):
    # files = {
    #     "genuine_firewall": "genuine_firewall_logs.txt",
    #     "scam_firewall": "scam_firewall_logs.txt",
    #     "genuine_network": "genuine_network_logs.txt",
    #     "scam_network": "scam_network_logs.txt",
    #     "genuine_web": "genuine_web_logs.txt",
    #     "scam_web": "scam_web_logs.txt",
    #     "genuine_app": "genuine_app_logs.txt",
    #     "scam_app": "scam_app_logs.txt"
    # }


    # for _ in range(log_count):

    #     with open(files["genuine_firewall"], "a") as f:
    #         f.write(generate_genuine_firewall_log() + '\n')
    #     with open(files["scam_firewall"], "a") as f:
    #         f.write(generate_scam_firewall_log() + '\n')
    #     with open(files["genuine_network"], "a") as f:
    #         f.write(generate_genuine_network_log() + '\n')
    #     with open(files["scam_network"], "a") as f:
    #         f.write(generate_scam_network_log() + '\n')
    #     with open(files["genuine_web"], "a") as f:
    #         f.write(generate_genuine_web_log() + '\n')
    #     with open(files["scam_web"], "a") as f:
    #         f.write(generate_scam_web_log() + '\n')
    #     with open(files["genuine_app"], "a") as f:
    #         f.write(generate_genuine_app_log() + '\n')
    #     with open(files["scam_app"], "a") as f:
    #         f.write(generate_scam_app_log() + '\n')
    
    with open(os.path.join("logs", "test_scam_firewall_logs.txt"), "a", encoding="utf-8") as f:
        for _ in range(100):
            f.write(generate_scam_firewall_log() + '\n')

    time.sleep(delay)



# Run the log generator
if __name__ == "__main__":
    generate_logs(log_count=100000, delay=2)
