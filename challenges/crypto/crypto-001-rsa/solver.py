# ── solver.py  (solution — do NOT give to players) ──
import math

c = 148456361628992144539540754444784478402898681038990893026358720730496679423064

def icbrt(n):
    # Integer cube root
    if n < 0: return -icbrt(-n)
    x = int(round(n ** (1/3)))
    for i in [x-2,x-1,x,x+1,x+2]:
        if i**3 == n: return i
    # Newton's method for large numbers
    x = n
    while True:
        x1 = (2*x + n//(x*x)) // 3
        if x1 >= x: break
        x = x1
    return x

m = icbrt(c)
flag = m.to_bytes((m.bit_length()+7)//8, 'big').decode()
print("Flag:", flag)
# Output: CTF{rs4_sm4ll_exp0n3nt_cub3_r00t}