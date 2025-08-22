# basic-mod2
---
#### A new modular challenge! Download the message here. Take each number mod 41 and find the modular inverse for the result. Then map to the following character set: 1-26 are the alphabet, 27-36 are the decimal digits, and 37 is an underscore. Wrap your decrypted message in the picoCTF flag format (i.e. picoCTF{decrypted_message})
---
Bài này thì không khác gì so với bài basic-mod1, nhưng có dùng cả modulo nghịch đảo.
### Modulo nghịch đảo là gì?
Nghịch đảo của a mod n là x sao cho:
&nbsp;&nbsp;&nbsp;&nbsp;$a \times x \equiv 1 \enspace (mod \enspace n)$

---
Phần code trong file py
```picoCTF{1NV3R53LY_H4RD_C680BDC1}```