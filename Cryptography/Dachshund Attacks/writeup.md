# Dachshund Attacks
---
#### What if d is too small? Connect with nc mercury.picoctf.net 62786.

---
Bài này cho ảnh con chó không biết để làm gì, ta sẽ đi vào nc mercury.picoctf.net 62786.

Cho n, e, c và ta thấy e rất lớn. Do đó ta có thể xem xét trường hợp dùng Wiener Attack.

### Wiener Attack

Thời gian mã hóa phụ thuộc vào độ lớn của e, trong khi thời gian giải mã phụ thuộc độ lớn của d. Để giảm thời gian giải mã (ví dụ trong các tác vụ của 1 smartcard với CPU giới hạn), người ta thường chọn d nhỏ. Thế nhưng việc chọn d nhỏ lại khiến cho hệ thống trở nên yếu đi và có thể bị phá vỡ hoàn toàn bởi phương pháp tấn công Wiener Attack.
Điều kiện cần:
```
d < 1/3 n¼
q < p < 2q
e' < n3/2 với e' = e (mod n) hay Public Key không quá lớn
```

Template của Wierner Attack (cre: Cryptobook):
```python
#!/usr/bin/env python3
import owiener
from Crypto.Util.number import long_to_bytes

#--------Data--------#

N = <N>
e = <e>
c = <c>

#--------Wiener's attack--------#

d = owiener.attack(e, N)

if d:
    m = pow(c, d, N)
    flag = long_to_bytes(m).decode()
    print(flag)
else:
    print("Wiener's Attack failed.")
```