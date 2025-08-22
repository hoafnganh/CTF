# Easy Peasy
---
#### A one-time pad is unbreakable, but can you manage to recover the flag? (Wrap with picoCTF{}) nc mercury.picoctf.net 20266 otp.py

---
Đọc file ta thấy độ dài của KEY là 50000, còn độ dài của encrypt flag là 32, do đó ta sẽ chèn thêm 50000 - 32 = 49968 kí tự a nữa để chạy hết lượt key đó.

Sau khi KEY chạy hết 1 lượt, ta lại thử thêm 32 kí tự a(bằng đúng số ký tự của flag) để tìm ra giải mã.
plaintext_a = 'a' * 32
enc_a = key ^ plaintext_a
Mà ta có enc_flag = key ^ plaintext_flag
Từ đó suy ra plaintext_flag = enc_flag ^ key = enc_flag ^ enc_a ^ plaintext_a