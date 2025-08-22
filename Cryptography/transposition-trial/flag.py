s = "heTfl g as iicpCTo{7F4NRP051N5_16_35P3X51N3_V6E5926A}4"

# Chia thành block 3 ký tự
blocks = [s[i:i+3] for i in range(0, len(s), 3)]

# Áp dụng quy luật: đưa ký tự cuối lên đầu
decoded = ''.join(b[-1] + b[0] + b[1] for b in blocks if len(b) == 3)

print("Decoded:", decoded)
