with open(r'D:\CTF\picoCTF\Cryptography\basic-mod2\message.txt', 'r') as f:
    data = f.read()

lst = list(map(int, data.strip().split()))

s = ""
for i in lst:
    m = pow(i % 41, -1, 41)
    if m >= 1 and m <= 26:
        s += chr(m - 1 + ord('A'))
    elif m >= 27 and m <= 36:
        s += str(m - 27)
    else:
        s += '_'
print(s)


