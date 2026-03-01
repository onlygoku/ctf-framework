import sys
SECRET = [ord(c) ^ 0x42 for c in "CTF{8b4ba8a2b26b70da438de6c3}"]

def check(inp):
    return len(inp) == len(SECRET) and all(ord(c)^0x42==s for c,s in zip(inp, SECRET))

if __name__ == "__main__":
    inp = input("Enter the flag: ")
    print("Correct!" if check(inp) else "Wrong!")
