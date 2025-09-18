import requests
import time
import platform
import socket

device_name = platform.node()

def discover_server():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp.settimeout(5)
    udp.sendto(b"DISCOVER_SERVER", ("<broadcast>", 54545))

    try:
        data, addr = udp.recvfrom(1024)
        if data == b"SERVER_HERE":
            return addr[0]
    except socket.timeout:
        return None

def send_logs(server_ip):
    url = f"http://{server_ip}:5000/log"
    logs = [
        "System booted",
        "User clicked scam link",
        "Suspicious download",
        "Normal login activity"
    ]
    while True:
        log = logs[int(time.time()) % len(logs)]
        try:
            requests.post(url, json={"device": device_name, "log": log})
        except:
            pass
        time.sleep(10)

if __name__ == "__main__":
    server_ip = discover_server()
    if server_ip:
        send_logs(server_ip)
