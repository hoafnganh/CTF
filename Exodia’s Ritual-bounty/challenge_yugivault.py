# -*- coding: utf-8 -*-
import json, os, random, hashlib, uuid, re
from typing import List, Dict

HERE = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(HERE, os.environ.get("DATA_FILE", "yugioh.json"))

from ecc_secp256k1 import public_key_compressed, ecdsa_sign_raw

def _sha256(b: bytes) -> bytes: return hashlib.sha256(b).digest()
def _hex(b: bytes) -> str: return b.hex()

def _pack_nonce_from_ids_shuffled(ids: List[int]) -> bytes:
    buf = bytearray(32)
    for i in range(12):
        v = int(ids[i]) & 0xFFFF
        buf[i*2:i*2+2] = v.to_bytes(2, 'little')
    buf.reverse()
    return bytes(buf)

class YugiVaultChallenge:
    def __init__(self):
        self.dataset = self._load_dataset()
        self.secret_order: List[Dict] = None
        self.selected_sorted: List[Dict] = None
        self.private_key: bytes = None
        self.public_key: bytes = None
        self._vaults = None

    def _load_dataset(self):
        data = json.load(open(DATASET_PATH, "r", encoding="utf-8"))
        cleaned = []
        for it in data:
            if isinstance(it, dict) and "name" in it and ("power" in it or "id" in it):
                v = int(it.get("power", it.get("id")))
                cleaned.append({"id": v, "name": str(it["name"])})
        cleaned.sort(key=lambda x: x["id"])
        if len(cleaned) < 12:
            raise RuntimeError("dataset phải có ≥ 12 lá Yu-Gi-Oh!")
        return cleaned

    def start(self):
        pool = self.dataset[:]
        random.shuffle(pool)
        self.secret_order = pool[:12]
        ids_secret = [p["id"] for p in self.secret_order]
        pk_material = bytes([x & 0xFF for x in ids_secret])
        self.private_key = _sha256(pk_material)
        self.public_key = public_key_compressed(self.private_key)
        self.selected_sorted = sorted(self.secret_order, key=lambda x: x["id"])
        self._vaults = self._make_vaults(ids_secret)

    def get_public_key_hex(self) -> str:
        if not self.public_key: raise RuntimeError("Chưa start challenge")
        return _hex(self.public_key)

    def get_selected_cards(self) -> List[Dict]:
        if not self.selected_sorted: raise RuntimeError("Chưa start challenge")
        return self.selected_sorted

    def _make_vaults(self, ids_secret: List[int]):
        NUM_VAULTS = 6
        vaults = []
        for _ in range(NUM_VAULTS):
            v_id = str(uuid.uuid4())
            shuffled = ids_secret[:]
            random.shuffle(shuffled)
            nonce = _pack_nonce_from_ids_shuffled(shuffled)
            msg_hash = _sha256(v_id.encode("utf-8"))
            sig_raw = ecdsa_sign_raw(msg_hash, self.private_key, nonce)  # raw r||s 64B
            vaults.append({"id": v_id, "signature": _hex(sig_raw)})
        return vaults

    def get_vaults(self):
        if self._vaults is None: raise RuntimeError("Chưa start challenge")
        return self._vaults

    # ==== Exodia: 5 mảnh XOR ra private_key (32B) ====
    def _parse_hex_to_32(self, s: str) -> bytes:
        b = bytes.fromhex(s.strip())
        if len(b) > 32:
            raise ValueError("quá 32 byte")
        return b.rjust(32, b"\x00")

    def _d_bytes(self) -> bytes:
        return self.private_key

    def verify_exodia_shards(self, head, left_arm, right_arm, left_leg, right_leg):
        try:
            parts = [self._parse_hex_to_32(x) for x in (head, left_arm, right_arm, left_leg, right_leg)]
        except Exception:
            return False, "Mỗi mảnh Exodia phải là hex (≤32 byte)"
        acc = bytes(32)
        for p in parts:
            acc = bytes(a ^ b for (a,b) in zip(acc, p))
        ok = (acc == self._d_bytes())
        return ok, ("Exodia assembled!" if ok else "Exodia chưa đủ/không khớp")
