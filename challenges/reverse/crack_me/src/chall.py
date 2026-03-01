import sys
SECRET = [ord(c) ^ 0x42 for c in "CTF{0ba92b42519375d420997dc2}"]

def check(inp):
    return len(inp) == len(SECRET) and all(ord(c)^0x42==s for c,s in zip(inp, SECRET))

if __name__ == "__main__":
    inp = input("Enter the flag: ")
    print("Correct!" if check(inp) else "Wrong!")
