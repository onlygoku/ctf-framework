from Crypto.Util.number import getPrime, bytes_to_long

FLAG = b"CTF{a20ed01ee85b04893c04cd9c}"

def encrypt(msg):
    p, q = getPrime(512), getPrime(512)
    n = p * q
    e = 65537
    c = pow(bytes_to_long(msg), e, n)
    return {"n": n, "e": e, "c": c}

result = encrypt(FLAG)
print(f"n = {result['n']}")
print(f"e = {result['e']}")
print(f"c = {result['c']}")
