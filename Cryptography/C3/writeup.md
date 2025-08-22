# C3
---

#### This is the Custom Cyclical Cipher! Download the ciphertext here. Download the encoder here. Enclose the flag in our wrapper for submission. If the flag was "example" you would submit "picoCTF{example}".
---
Khi ta chạy file encoder, ta nhận thấy rằng file chưa thể chạy.
Ta dễ thấy rằng ciphertext có kí tự đầu là "DLS..." thế nên khi tới dòng 14 thì code sẽ kẹt vì lookup1 không chứa D.
Ta phải sửa lại code 1 chút.

```python
import sys

ciphertext = 'DLSeGAGDgBNJDQJDCFSFnRBIDjgHoDFCFtHDgJpiHtGDmMAQFnRBJKkBAsTMrsPSDDnEFCFtIbEDtDCIbFCFtHTJDKerFldbFObFCFtLBFkBAAAPFnRBJGEkerFlcPgKkImHnIlATJDKbTbFOkdNnsgbnJRMFnRBNAFkBAAAbrcbTKAkOgFpOgFpOpkBAAAAAAAiClFGIPFnRBaKliCgClFGtIBAAAAAAAOgGEkImHnIl'

lookup1 = "\n \"#()*+/1:=[]abcdefghijklmnopqrstuvwxyz"
lookup2 = "ABCDEFGHIJKLMNOPQRSTabcdefghijklmnopqrst"

out = ""

prev = 0
for char in ciphertext:
  cur = lookup2.index(char)
  index = (cur + prev) % len(lookup1)
  out += lookup1[index]
  prev = index

sys.stdout.write(out)
```

Khi chạy ta sẽ được file encode đúng.
```
# Gọi file này là convert2.txt
#asciiorder
#fortychars
#selfinput
#pythontwo

chars = ""
from fileinput import input
for line in input():
    chars += line
b = 1 / 1

for i in range(len(chars)):
    if i == b * b * b:
        print chars[i] #prints
        b += 1 / 1
```
Sửa code 1 chút về python3
```python
# Gọi file này là decrypt.py
#asciiorder
#fortychars
#selfinput
#pythontwo

chars = ""
from fileinput import input
for line in input():
    chars += line
b = 1 / 1

for i in range(len(chars)):
    if i == b * b * b:
        print(chars[i], end = '') #prints
        b += 1 / 1

print()
```

dùng lệnh ```cat convert2.txt | python3 decrypt.py``` thì ta sẽ ra đáp án.


