#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, json, socket, socketserver, time
from challenge_yugivault import YugiVaultChallenge

BANNER = (
    "\n========================================================================================\n"
    "                                  YugiVault — Exodia \n"
    "========================================================================================\n"
    "Lệnh: help | public_key | choices | vaults | unlock_exodia <head> <Larm> <Rarm> <Lleg> <Rleg> | quit\n"
)

DEFAULT_PORT = int(os.environ.get("PORT", "41337"))
HOST = "0.0.0.0"
READLINE_MAXLEN = 1024
MAX_REQUESTS = 200
SESSION_TIMEOUT = 180

def safe_send(wfile, s: str) -> None:
    try:
        if not s.endswith("\n"):
            s += "\n"
        wfile.write(s.encode("utf-8", errors="ignore"))
        wfile.flush()
    except Exception:
        pass

def parse_args(line: str):
    parts = line.strip().split()
    cmd = parts[0].lower() if parts else ""
    args = parts[1:]
    return cmd, args

class ClientSession:
    def __init__(self):
        self.challenge = None
        self.start_ts = time.time()
        self.requests = 0
    def autostart(self):
        if self.challenge is None:
            self.challenge = YugiVaultChallenge()
            self.challenge.start()

class Handler(socketserver.StreamRequestHandler):
    def setup(self):
        super().setup()
        try: self.request.settimeout(1800.0)
        except Exception: pass
        self.session = ClientSession()
        self.session.autostart()
    def handle(self):
        safe_send(self.wfile, BANNER)
        while True:
            if time.time() - self.session.start_ts > SESSION_TIMEOUT:
                safe_send(self.wfile, "Hết thời gian phiên. Tạm biệt!"); break
            safe_send(self.wfile, "> ")
            try:
                line = self.rfile.readline(READLINE_MAXLEN + 1)
            except socket.timeout:
                safe_send(self.wfile, "Timeout khi chờ lệnh."); break
            except Exception:
                break
            if not line: break
            if len(line) > READLINE_MAXLEN:
                safe_send(self.wfile, f"Dòng nhập quá dài (> {READLINE_MAXLEN})."); break
            decoded = line.decode("utf-8", errors="ignore").strip()
            if not decoded: continue
            self.session.requests += 1
            if self.session.requests > MAX_REQUESTS:
                safe_send(self.wfile, "Quá số lượng lệnh cho phép. Bye!"); break
            cmd, args = parse_args(decoded)
            if cmd in ("quit", "exit"):
                safe_send(self.wfile, "Tạm biệt!"); break
            elif cmd == "help":
                safe_send(self.wfile, "Lệnh:")
                safe_send(self.wfile, "  public_key  - in public key (hex)")
                safe_send(self.wfile, "  choices     - 12 lá Yu-Gi-Oh! (đã sort theo Power)")
                safe_send(self.wfile, "  vaults      - 6 vault id + chữ ký (r||s)")
                safe_send(self.wfile, "  unlock_exodia <head> <Larm> <Rarm> <Lleg> <Rleg>")
                safe_send(self.wfile, "  quit/exit   - thoát")
            elif cmd == "public_key":
                safe_send(self.wfile, f"public_key: {self.session.challenge.get_public_key_hex()}")
            elif cmd == "choices":
                try:
                    cps = self.session.challenge.get_selected_cards()
                    safe_send(self.wfile, json.dumps(cps, ensure_ascii=False))
                except Exception as e:
                    safe_send(self.wfile, f"Lỗi: {e}")
            elif cmd == "vaults":
                try:
                    v = self.session.challenge.get_vaults()
                    safe_send(self.wfile, json.dumps(v, ensure_ascii=False))
                except Exception as e:
                    safe_send(self.wfile, f"Lỗi: {e}")
            elif cmd == "unlock_exodia":
                if len(args) != 5:
                    safe_send(self.wfile, "Cú pháp: unlock_exodia <head> <Larm> <Rarm> <Lleg> <Rleg>")
                else:
                    ok, msg = self.session.challenge.verify_exodia_shards(*args)
                    if ok:
                        flag = os.environ.get("FLAG", "PTITCTF{demo_flag}")
                        safe_send(self.wfile, msg)
                        safe_send(self.wfile, f"FLAG: {flag}")
                        break
                    else:
                        safe_send(self.wfile, msg)
            else:
                safe_send(self.wfile, "Lệnh không hợp lệ. Gõ 'help'.")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

def main():
    with ThreadedTCPServer((HOST, DEFAULT_PORT), Handler) as server:
        print(f"[+] Listening on {HOST}:{DEFAULT_PORT}")
        server.serve_forever()

if __name__ == "__main__":
    main()
