# Buffer Overflow - Binary Exploitation

## Description
A vulnerable C binary is running on the server. There is no stack canary and no PIE. Overflow the buffer and hijack execution to call the win() function.

## Connection
`nc challenge.ctf.local 10003`

## Flag
`CTF{CTF{03b41ca277be8e0d1513aa4f}}`
