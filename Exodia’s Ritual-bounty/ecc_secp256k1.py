# -*- coding: utf-8 -*-
from typing import Tuple
P  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
A  = 0
B  = 7
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
G  = (Gx, Gy)

def _mod_inv(a: int, n: int) -> int:
    if a == 0: raise ZeroDivisionError("inverse of 0")
    lm, hm = 1, 0; low, high = a % n, n
    while low > 1:
        r = high // low
        nm, new = hm - lm * r, high - low * r
        lm, low, hm, high = nm, new, lm, low
    return lm % n

def _point_add(Pt, Qt):
    if Pt is None: return Qt
    if Qt is None: return Pt
    x1, y1 = Pt; x2, y2 = Qt
    if x1 == x2 and (y1 + y2) % P == 0: return None
    if Pt == Qt:
        s = ((3*x1*x1 + A) * _mod_inv(2*y1 % P, P)) % P
    else:
        s = ((y2 - y1) * _mod_inv((x2 - x1) % P, P)) % P
    x3 = (s*s - x1 - x2) % P
    y3 = (s*(x1 - x3) - y1) % P
    return (x3, y3)

def _scalar_mult(k: int, Pt=G):
    if k % N == 0 or Pt is None: return None
    if k < 0: return _scalar_mult(-k, (Pt[0], (-Pt[1]) % P))
    result = None; addend = Pt
    while k:
        if k & 1: result = _point_add(result, addend)
        addend = _point_add(addend, addend)
        k >>= 1
    return result

def public_key_compressed(privkey: bytes) -> bytes:
    d = int.from_bytes(privkey, 'big'); assert 1 <= d < N
    Px, Py = _scalar_mult(d, G)
    return bytes([0x02 if (Py % 2 == 0) else 0x03]) + Px.to_bytes(32, 'big')

def ecdsa_sign_raw(msg32: bytes, privkey: bytes, k_bytes: bytes) -> bytes:
    assert len(msg32) == 32
    d = int.from_bytes(privkey, 'big'); assert 1 <= d < N
    k = int.from_bytes(k_bytes, 'big') % N or 1
    Rx, Ry = _scalar_mult(k, G)
    r = Rx % N or 1
    z = int.from_bytes(msg32, 'big') % N
    s = (_mod_inv(k, N) * (z + r * d)) % N or 1
    if s > N // 2:  # low-s
        s = N - s
    return r.to_bytes(32, 'big') + s.to_bytes(32, 'big')
