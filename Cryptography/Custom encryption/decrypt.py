# from random import randint
# import sys


# ct = [131553, 993956, 964722, 1359381, 43851, 1169360, 950105, 321574, 1081658, 613914, 0, 1213211, 306957, 73085, 993956, 0, 321574, 1257062, 14617, 906254, 350808, 394659, 87702, 87702, 248489, 87702, 380042, 745467, 467744, 716233, 380042, 102319, 175404, 248489]



# def generator(g, x, p):
#     return pow(g, x, p)


# def xor_decrypt(plaintext, text_key):
#     cipher_text = ""
#     key_length = len(text_key)
#     for i, char in enumerate(plaintext[::-1]):  # đảo ở mã hóa
#         key_char = text_key[i % key_length]
#         encrypted_char = chr(ord(char) ^ ord(key_char))
#         cipher_text += encrypted_char
#     return cipher_text


# def decrypt(cipher, key, text_key):
#     semi_plain = ""
#     for num in cipher:
#         ascii_code = round(num / (key * 311))
#         semi_plain += chr(ascii_code)
#     decrypted_text = xor_decrypt(semi_plain, text_key)
#     return decrypted_text


# # ==== Test chuẩn ====
# original_message = "hello_world_123"
# text_key = "trudeau"
# a = 94
# b = 21
# p = 97
# g = 31

# v = generator(g, b, p)
# key = generator(v, a, p)
# print("Shared key:", key)  # phải là 47


# # Decrypt
# plain = decrypt(ct, key, text_key)
# print("Decrypted:", plain)

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
