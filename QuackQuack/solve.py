#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import re
import hashlib
import random

HOST = "103.197.184.48"
PORT = 31337

ROUNDS_TOTAL = 30
DUCKS_START  = 3
INC          = True

BITS = 20
MOD16 = 1 << 16
TRACK_LEN_DEFAULT = 60

def sha1_hex(x: int) -> str:
    return hashlib.sha1(str(x).encode()).hexdigest()

def derive_int(*parts, bits=64):
    h = hashlib.sha1()
    for p in parts:
        h.update(str(p).encode()); h.update(b"|")
    return int.from_bytes(h.digest(), "big") & ((1 << bits) - 1)

TILE_NORMAL, TILE_BOOST, TILE_MUD, TILE_OIL = ".", "B", "M", "O"

class FancyTrack:
    def __init__(self, seed, lane, length):
        rng = random.Random(derive_int("track", seed, lane, length, bits=64))
        self.tiles = []
        for _ in range(length):
            r = rng.random()
            self.tiles.append(
                TILE_BOOST if r < 0.06 else
                TILE_MUD   if r < 0.11 else
                TILE_OIL   if r < 0.16 else
                TILE_NORMAL
            )
    def at(self, x, length):
        return self.tiles[x] if 0 <= x < length else TILE_NORMAL

class DuckEngine:
    def __init__(self, seed, n, length=TRACK_LEN_DEFAULT):
        self.rng = random.Random(seed)
        self.n, self.length = n, length
        self.x   = [0]*n
        self.cd  = [0]*n
        self.trk = [FancyTrack(seed, i, length) for i in range(n)]
        self.wind_bias = self.rng.random()*0.08
        self.wind_puff = self.rng.random()*0.05
        self.finish_eps = [
            (derive_int("finish_eps", seed, i, length, bits=64)/float(1<<64))*1e-6 + i*1e-9
            for i in range(n)
        ]

    def step_once(self):
        prev = self.x[:]
        for i in range(self.n):
            prog = self.x[i]/max(1, self.length)
            step = self.rng.choice([0,1,1,1,2] if prog < 0.7 else [0,1,1,1,1,2])
            if self.rng.random() < self.wind_bias: step += 1
            if self.rng.random() < self.wind_puff: step += 1
            if any(px - prev[i] in (1,2) for j, px in enumerate(prev) if j != i): step += 1
            tentative = min(self.length, self.x[i] + step)
            tile = self.trk[i].at(tentative, self.length)
            slip_p = 0.05 + (0.10 if tile == TILE_OIL else 0.0)
            if tile == TILE_BOOST: step += 1
            elif tile == TILE_MUD: step = max(0, step-1)
            if self.rng.random() < slip_p:
                self.x[i] = max(0, self.x[i]-1)
                if self.cd[i] > 0: self.cd[i] -= 1
                continue
            if self.cd[i] <= 0 and self.rng.random() < 0.08:
                step += 2
                self.cd[i] = self.rng.randint(10,16)
            self.x[i] = min(self.length, self.x[i] + step)
            if self.cd[i] > 0: self.cd[i] -= 1

    def winner_1based_eps(self):
        best_i, best_s = 0, -1e99
        for i in range(self.n):
            s = self.x[i] - (self.length + self.finish_eps[i])
            if s > best_s:
                best_s, best_i = s, i
        return best_i + 1

def find_seed_from_commit_ticket(commit_hex, ticket):
    inv = pow(31337, -1, MOD16)
    base = ((ticket - 1337) * inv) % MOD16
    for k in range(1 << (BITS - 16)):
        s = (base + k * MOD16) & ((1 << BITS) - 1)
        if sha1_hex(s) == commit_hex:
            return s
    return None

def compute_winner(seed, n, track_len=TRACK_LEN_DEFAULT):
    eng = DuckEngine(seed, n, track_len)
    while max(eng.x) < eng.length:
        eng.step_once()
    return eng.winner_1based_eps()

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
def strip_ansi(b: bytes) -> str:
    return ANSI_RE.sub("", b.decode("utf-8", errors="ignore"))

def recv_until_commit_ticket(sock):
    buf = ""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            raise RuntimeError("connection closed")
        buf += strip_ansi(chunk)
        if "Input không hợp lệ" in buf or "GG!" in buf or "FLAG:" in buf:
            return buf, None, None
        m1 = re.search(r"COMMIT:\s*([0-9a-f]{40})", buf)
        m2 = re.search(r"TICKET:\s*(\d+)", buf)
        if m1 and m2:
            return buf, m1.group(1), int(m2.group(1))

def recv_until_next_round_or_end(sock):
    buf = ""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += strip_ansi(chunk)
        if "Round " in buf or "FLAG:" in buf or "GG!" in buf or "Input không hợp lệ" in buf:
            break
    return buf

def main():
    s = socket.socket()
    s.settimeout(90)
    s.connect((HOST, PORT))
    r = 1
    while True:
        text, commit, ticket = recv_until_commit_ticket(s)
        print(text, end="")
        if commit is None:
            break
        n = DUCKS_START + (r-1 if INC else 0)
        seed = find_seed_from_commit_ticket(commit, ticket)
        if seed is None:
            raise RuntimeError("Seed not found from commit+ticket")
        win = compute_winner(seed, n)
        print(f"[round {r}] commit={commit[:8]} ticket={ticket} -> seed={seed} → bet lane {win}")
        s.sendall((str(win) + "\n").encode())
        out = recv_until_next_round_or_end(s)
        print(out, end="")
        if "FLAG:" in out or "GG!" in out or "Input không hợp lệ" in out:
            break
        r += 1
        if ROUNDS_TOTAL and r > ROUNDS_TOTAL + 2:
            break

if __name__ == "__main__":
    main()
