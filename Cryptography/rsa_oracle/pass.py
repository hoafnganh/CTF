from pwn import *
from Crypto.Util.number import long_to_bytes, bytes_to_long

enc = 2336150584734702647514724021470643922433811330098144930425575029773908475892259185520495303353109615046654428965662643241365308392679139063000973730368839
conn = remote('titan.picoctf.net', 63518)


def d(cipher):
    conn.sendlineafter(b'decrypt.', b'D')
    conn.sendlineafter(b': ', str(cipher).encode())
    try:
        conn.recvuntil(b'mod n): ')
        dec = conn.recvline().strip().decode()
        if len(dec) % 2 != 0:
            dec = '0' + dec
        dec = bytes.fromhex(dec)
        return bytes_to_long(dec)
    except EOFError:
        return None


def e(cipher):
    conn.sendlineafter(b'decrypt.', b'E')
    conn.sendlineafter(b': ', long_to_bytes(cipher))
    conn.recvuntil(b'mod n) ')
    dec = conn.recvline().strip().decode()
    return int(dec)



print(long_to_bytes(d((enc*e(2)))//2))
conn.close()

# 60f50