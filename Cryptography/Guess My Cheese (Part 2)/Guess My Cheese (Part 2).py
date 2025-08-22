#!/usr/bin/env python3
import hashlib
import sys

target_hash = "051f63ad38585e065ffcb6de350477bdb6643177a0104dc9a04f4f33ce6cb703"

# Define the encodings and case variants we want to try.
encodings = ["utf-8", "utf-16-le", "utf-16-be", "latin-1"]
case_variants = {
    "original": lambda s: s,
    "lower": lambda s: s.lower(),
    "upper": lambda s: s.upper(),
}

# Read cheese names from cheese_list.txt (one per line)
try:
    with open("D:\cheese_list.txt", "r") as f:
        cheeses = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("cheese_list.txt not found. Please create it with your list of cheese names.")
    sys.exit(1)

found = False

# Define a helper function that tests a candidate bytes object.
def test_candidate(candidate_bytes, method, extra, cheese, case_name, enc, salt):
    global found
    hash_val = hashlib.sha256(candidate_bytes).hexdigest()
    if hash_val == target_hash:
        print("Match found!")
        print(f"Cheese: {cheese}  (case variant: {case_name}, encoding: {enc})")
        print(f"Salt value: {salt} (0x{salt:02x})")
        print(f"Method: {method}, extra: {extra}")
        try:
            candidate_str = candidate_bytes.decode(enc)
        except Exception:
            candidate_str = repr(candidate_bytes)
        print(f"Candidate (using {enc}): {candidate_str}")
        found = True
        return True
    return False

for cheese in cheeses:
    for case_name, case_func in case_variants.items():
        cheese_variant = case_func(cheese)
        for enc in encodings:
            try:
                cheese_bytes = cheese_variant.encode(enc)
            except Exception:
                continue
            for salt in range(256):
                salt_raw = bytes([salt])
                salt_hex_str = format(salt, "02x")
                try:
                    salt_hex = salt_hex_str.encode(enc)
                except Exception:
                    salt_hex = salt_hex_str.encode("utf-8")  # fallback

                # Option A: Append and prepend raw byte.
                if test_candidate(cheese_bytes + salt_raw, "append_raw", "raw byte appended",
                                  cheese, case_name, enc, salt):
                    break
                if test_candidate(salt_raw + cheese_bytes, "prepend_raw", "raw byte prepended",
                                  cheese, case_name, enc, salt):
                    break

                # Option B: Append and prepend hex string.
                if test_candidate(cheese_bytes + salt_hex, "append_hex", "hex string appended",
                                  cheese, case_name, enc, salt):
                    break
                if test_candidate(salt_hex + cheese_bytes, "prepend_hex", "hex string prepended",
                                  cheese, case_name, enc, salt):
                    break

                # Option C: Insert raw byte at every possible index.
                for i in range(len(cheese_bytes) + 1):
                    candidate = cheese_bytes[:i] + salt_raw + cheese_bytes[i:]
                    if test_candidate(candidate, "insert_raw", f"at byte index {i}",
                                      cheese, case_name, enc, salt):
                        break
                else:
                    pass
                if found:
                    break

                # Option D: Insert hex string at every possible index.
                for i in range(len(cheese_bytes) + 1):
                    candidate = cheese_bytes[:i] + salt_hex + cheese_bytes[i:]
                    if test_candidate(candidate, "insert_hex", f"at byte index {i}",
                                      cheese, case_name, enc, salt):
                        break
                else:
                    pass
                if found:
                    break
            if found:
                break
        if found:
            break
    if found:
        break

if not found:
    print("No matching cheese and salt combination was found.")