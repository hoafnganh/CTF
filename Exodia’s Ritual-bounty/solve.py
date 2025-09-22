# -*- coding: utf-8 -*-
from collections import defaultdict
import socket, json, hashlib, secrets, itertools, sys, re, time
from typing import List, Tuple, Dict, Optional

# secp256k1
P  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
A  = 0
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
G  = (Gx, Gy)

def _mod_inv(a: int, n: int) -> int:
    if a == 0: raise ZeroDivisionError("inverse of 0")
    lm, hm = 1, 0; low, high = a % n, n
    while low > 1:
        r = high // low
        nm, new = hm - lm*r, high - low*r
        lm, low, hm, high = nm, new, lm, low
    return lm % n

def _point_add(Pt, Qt):
    if Pt is None: return Qt
    if Qt is None: return Pt
    x1, y1 = Pt; x2, y2 = Qt
    if Pt == Qt:
        if y1 % P == 0: return None
        s = ((3*x1*x1 + A) * _mod_inv((2*y1) % P, P)) % P
    else:
        if x1 == x2 and (y1 + y2) % P == 0: return None
        denom = (x2 - x1) % P
        if denom == 0: return None
        s = ((y2 - y1) * _mod_inv(denom, P)) % P
    x3 = (s*s - x1 - x2) % P
    y3 = (s*(x1 - x3) - y1) % P
    return (x3, y3)

def _point_neg(Pt):
    if Pt is None: return None
    x, y = Pt
    return (x, (-y) % P)

def _scalar_mult(k: int, Pt=G):
    if k % N == 0 or Pt is None: return None
    if k < 0: return _scalar_mult(-k, (Pt[0], (-Pt[1]) % P))
    result = None; addend = Pt
    while k:
        if k & 1: result = _point_add(result, addend)
        addend = _point_add(addend, addend)
        k >>= 1
    return result

def sha256i(b: bytes) -> int:
    return int.from_bytes(hashlib.sha256(b).digest(), 'big') % N

def parse_sig_r_s(sig_hex: str) -> Tuple[int,int]:
    sig = bytes.fromhex(sig_hex); assert len(sig) == 64
    return int.from_bytes(sig[:32],'big'), int.from_bytes(sig[32:],'big')

def recover_d_from_k_r_s_z(k: int, r: int, s: int, z: int) -> int:
    rinv = _mod_inv(r % N, N)
    return ((s * (k % N) - (z % N)) % N) * rinv % N

def pubkey_compressed_from_d(d: int) -> bytes:
    Px, Py = _scalar_mult(d, G)
    return (b'\x02' if (Py % 2 == 0) else b'\x03') + Px.to_bytes(32, 'big')

def lift_x_to_points(x: int):
    rhs = (pow(x % P, 3, P) + 7) % P
    y = pow(rhs, (P+1)//4, P)
    if (y*y) % P != rhs: return []
    return [(x % P, y), (x % P, (-y) % P)]

def k_bytes_from_order(words16_by_pos: List[int]) -> bytes:
    tail = b''.join(int(w).to_bytes(2, 'big') for w in words16_by_pos[::-1])
    return b'\x00'*8 + tail

B16 = 1 << 16

def precompute_Qj() -> List[Tuple[int,int]]:
    Q = []; powB = 1
    for _ in range(12):
        Q.append(_scalar_mult(powB % N, G))
        powB = (powB * B16) % N
    return Q

def mul_small_on_point(w: int, Pt: Tuple[int,int]) -> Tuple[int,int]:
    return _scalar_mult(w, Pt)

def build_high_map(words16: List[int], Q: List[Tuple[int,int]]):
    pos_hi = (6, 7, 8, 9, 10, 11)
    n = len(words16)
    contrib = [[mul_small_on_point(words16[i], Q[pos_hi[level]]) for level in range(6)] for i in range(n)]
    high_map = defaultdict(list)
    used = [False]*n
    cur_perm = [0]*6
    def dfs(level, acc_point):
        if level == 6:
            perm = tuple(cur_perm)
            high_map[acc_point].append((perm, frozenset(perm)))
            return
        for i in range(n):
            if not used[i]:
                used[i] = True
                cur_perm[level] = words16[i]
                term = contrib[i][level]
                new_acc = term if acc_point is None else _point_add(acc_point, term)
                dfs(level+1, new_acc)
                used[i] = False
    dfs(0, None)
    return high_map

def find_k_with_mitm_using_map(r: int, words16: List[int], Q: List[Tuple[int,int]], high_map) -> Tuple[Optional[int], Optional[List[int]]]:
    pos_lo = (0, 1, 2, 3, 4, 5); pos_hi = (6, 7, 8, 9, 10, 11)
    Rcands = lift_x_to_points(r % N)
    if not Rcands: return None, None
    words16 = tuple(words16); n = len(words16)
    contrib = [[mul_small_on_point(words16[i], Q[pos_lo[lvl]]) for lvl in range(6)] for i in range(n)]
    used = [False]*n
    cur_perm_lo = [0]*6
    for Rpt in Rcands:
        def dfs(level, acc_point):
            if level == 6:
                set_lo = frozenset(cur_perm_lo)
                target = _point_add(Rpt, _point_neg(acc_point))
                cands = high_map.get(target)
                if not cands: return
                for perm_hi, set_hi in cands:
                    if not set_hi.isdisjoint(set_lo):  # must be disjoint
                        continue
                    by_pos = [None]*12
                    for w,j in zip(cur_perm_lo, pos_lo): by_pos[j] = w
                    for w,j in zip(perm_hi,  pos_hi): by_pos[j] = w
                    k_bytes = k_bytes_from_order(by_pos)
                    k = int.from_bytes(k_bytes, 'big') % N
                    Rchk = _scalar_mult(k, G)
                    if Rchk is None or (Rchk[0] % N) != (r % N):
                        continue
                    raise StopIteration((k, by_pos))
                return
            for i in range(n):
                if not used[i]:
                    used[i] = True
                    cur_perm_lo[level] = words16[i]
                    term = contrib[i][level]
                    new_acc = term if acc_point is None else _point_add(acc_point, term)
                    dfs(level+1, new_acc)
                    used[i] = False
        try:
            dfs(0, None)
        except StopIteration as e:
            return e.value
    return None, None

def make_exodia_shards(d: int) -> List[str]:
    d_bytes = d.to_bytes(32, 'big')
    parts = [secrets.token_bytes(32) for _ in range(4)]
    x = d_bytes
    for p in parts: x = bytes(a ^ b for a,b in zip(x, p))
    parts.append(x)
    return [p.hex() for p in parts]

def recvline(sock) -> str:
    buf = b""
    while not buf.endswith(b"\n"):
        chunk = sock.recv(1)
        if not chunk: break
        buf += chunk
    return buf.decode("utf-8", errors="ignore")

def read_until_prompt(sock):
    out = ""
    while True:
        line = recvline(sock)
        if not line: break
        out += line
        if line.endswith("> ") or line.strip().endswith(">"): break
    return out

def send_cmd(sock, cmd: str) -> str:
    sock.sendall((cmd+"\n").encode())
    return read_until_prompt(sock)

def parse_json_block(block: str):
    m = re.search(r'(\[[\s\S]*\])', block)
    if not m: m = re.search(r'(\{[\s\S]*\})', block)
    if not m: raise ValueError("Không tìm thấy JSON:\n" + block[-500:])
    return json.loads(m.group(1))

def solve(host: str, port: int, verbose: bool = True):
    t0 = time.time()
    with socket.create_connection((host, port), timeout=20) as s:
        _ = read_until_prompt(s)
        if verbose: print("[*] Getting public_key ...")
        pub_out = send_cmd(s, "public_key")
        m = re.search(r'public_key:\s*([0-9a-fA-F]+)', pub_out)
        pub_hex = m.group(1).lower() if m else None
        if verbose and pub_hex: print("[+] pub =", pub_hex)

        if verbose: print("[*] Getting choices ...")
        ch_out = send_cmd(s, "choices")
        choices = parse_json_block(ch_out)
        words16 = [int(c["id"]) & 0xFFFF for c in choices]
        if verbose: print("[+] 12 ids (16-bit) =", words16)

        if verbose: print("[*] Getting vaults ...")
        v_out = send_cmd(s, "vaults")
        vaults = parse_json_block(v_out)
        if verbose: print(f"[+] {len(vaults)} vaults fetched")

        if verbose: print("[*] Precomputing Q_j ...")
        Q = precompute_Qj()
        if verbose: print("[*] Building HIGH map ...")
        high_map = build_high_map(words16, Q)

        d = None
        for idx, v in enumerate(vaults):
            r, s_val = parse_sig_r_s(v["signature"])
            z = sha256i(v["id"].encode("utf-8"))
            if verbose: print(f"[*] Trying vault {idx+1}/{len(vaults)} ...")
            k, order = find_k_with_mitm_using_map(r, words16, Q, high_map)
            if k is None:
                if verbose: print("    [-] no k match")
                continue
            d_try = recover_d_from_k_r_s_z(k, r, s_val, z)
            if pub_hex:
                if pubkey_compressed_from_d(d_try).hex() != pub_hex:
                    if verbose: print("    [-] d mismatch pubkey")
                    continue
            d = d_try
            break

        if d is None:
            print("[-] Không khôi phục được d. Thử lại session mới.")
            return

        shards = make_exodia_shards(d)
        head, Larm, Rarm, Lleg, Rleg = shards
        if verbose: print("[*] Submitting unlock_exodia ...")
        res = send_cmd(s, f"unlock_exodia {head} {Larm} {Rarm} {Lleg} {Rleg}")
        print(res)
        if verbose: print(f"[✓] Done in {time.time()-t0:.2f}s")

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "103.197.184.48"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 41337
    try:
        solve(host, port, verbose=True)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
