# python3 -c "print('a'*49968);print('a'*32)" | nc mercury.picoctf.net 20266: chạy hết 1 vòng key để reset (50000 = 49968 + 32)

plain_a = 0x6161616161616161616161616161616161616161616161616161616161616161
enc_a = 0x0346071d3d1904593d1903573d1950033d1958592a3d1905593d1900573f3d19
enc_f = 0x5b1e564b6e415c0e394e0401384b08553a4e5c597b6d4a5c5a684d50013d6e4b

flag = "{:x}".format(enc_a ^ enc_f ^ plain_a)
print(bytes.fromhex(flag).decode("utf-8"))