# Custom encryption
---
#### Can you get sense of this code file and write the function that will decode the given encrypted file content. Find the encrypted file here flag_info and code file might be good to analyze and get the flag.

---

Họ cho code mã hoá, giờ chúng ta viết code giải mã ngược.

```python
def xor_decrypt(ciphertext, text_key):
    plain_text = ""
    key_length = len(text_key)
    for i, char in enumerate(ciphertext):
        key_char = text_key[i % key_length]
        decrypted_char = chr(ord(char) ^ ord(key_char))
        plain_text += decrypted_char
    return plain_text[::-1]  # đảo lại chuỗi đã bị đảo ở mã hóa

def decrypt(cipher, key, text_key):
    semi_plain = ""
    for num in cipher:
        if num == 0:
            semi_plain += chr(0)
        else:
            ascii_code = round(num / (key * 311))
            semi_plain += chr(ascii_code)
    decrypted_text = xor_decrypt(semi_plain, text_key)
    return decrypted_text

# ==== Thông số đã biết ====
ct = [131553, 993956, 964722, 1359381, 43851, 1169360, 950105, 321574, 1081658, 613914, 0, 1213211, 306957, 73085, 993956, 0, 321574, 1257062, 14617, 906254, 350808, 394659, 87702, 87702, 248489, 87702, 380042, 745467, 467744, 716233, 380042, 102319, 175404, 248489]
key = 47
text_key = "trudeau"

# ==== Thực thi ====
decrypted = decrypt(ct, key, text_key)
print("Decrypted:", decrypted)
```