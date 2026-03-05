"""
MISC-001: Saiyan Python Jail (Jail Escape)
Category: Misc | Difficulty: Advanced | Points: 450
Flag: CTF{j4il_3sc4p3_built1ns_byp4ss}

Run: python jail.py
Players get a restricted Python shell — must escape the sandbox.
"""
import sys, builtins

FLAG = "CTF{j4il_3sc4p3_built1ns_byp4ss}"

BANNED = [
    'import','__import__','exec','eval','open','os','sys',
    'subprocess','compile','globals','locals','vars',
    '__builtins__','__class__','__bases__','breakpoint'
]

def safe_eval(code, flag):
    # Restricted builtins
    safe_builtins = {
        'print': print,
        'len':   len,
        'range': range,
        'int':   int,
        'str':   str,
        'list':  list,
        'dict':  dict,
        'type':  type,
        'input': input,
    }
    for banned in BANNED:
        if banned in code:
            print(f"❌ '{banned}' is not allowed in the Hyperbolic Time Chamber!")
            return
    try:
        exec(code, {"__builtins__": safe_builtins, "power_level": 9001})
    except Exception as e:
        print(f"Error: {e}")

print("╔═══════════════════════════════════════════════╗")
print("║  HYPERBOLIC TIME CHAMBER — PYTHON JAIL v1.0  ║")
print("║  Escape the sandbox. Find the flag.           ║")
print("║  Type 'quit' to leave. Good luck, warrior.    ║")
print("╚═══════════════════════════════════════════════╝")
print()
print("Restricted shell active. Most builtins are disabled.")
print("Hint: you have access to 'type' and object introspection...\n")

while True:
    try:
        code = input("jail>>> ").strip()
        if code == "quit": break
        if not code: continue
        safe_eval(code, FLAG)
    except (EOFError, KeyboardInterrupt):
        break

# ══════════════════════════════════════════
# SOLUTION (one of many valid escapes):
#
# # Walk the MRO to get object, then subclasses
# ().__class__.__bases__[0].__subclasses__()
#
# # Find _wrap_close or WarningMessage that has os
# subs = ().__class__.__bases__[0].__subclasses__()
# for i,c in enumerate(subs):
#     if 'warning' in str(c).lower(): print(i,c)
#
# # Use __init__.__globals__ to get builtins back
# subs[INDEX].__init__.__globals__['__builtins__']
#
# # Or simpler — type() gives class, then:
# type(type(1))   # <class 'type'>
# (1).__class__.__mro__[-1].__subclasses__()
#
# Flag is stored in the server-side FLAG variable —
# once you have arbitrary code exec, read it from
# the running process or the source file.
# ══════════════════════════════════════════