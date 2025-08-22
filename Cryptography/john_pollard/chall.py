from sympy import isprime

n = 4966306421059967

# brute từ 2 đến sqrt(n)
for p in range(2, int(n ** 0.5) + 1):
    if n % p == 0:
        q = n // p
        if isprime(p) and isprime(q):
            print(f"[+] Found factors: p = {p}, q = {q}")
            break
