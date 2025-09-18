import socket

def run_responder():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", 54545))
    while True:
        data, addr = s.recvfrom(1024)
        if data == b"DISCOVER_SERVER":
            s.sendto(b"SERVER_HERE", addr)

if __name__ == "__main__":
    run_responder()
