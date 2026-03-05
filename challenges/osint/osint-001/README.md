# OSINT-001: Find Kakarot

**Category:** OSINT  
**Difficulty:** Intermediate  
**Points:** 200  
**Flag:** `CTF{0s1nt_k4k4r0t_f0und}`

## Briefing
Intelligence reports indicate that a Saiyan operative named **"Kakarot"**
has been hiding in plain sight on the internet.

We intercepted this partial profile:
- **Real name:** Son Goku  
- **Alias:** kakarot_saiyan  
- **Known email domain:** @capsulecorp.fake  
- **Left a message** somewhere online containing coordinates to his location

Your mission: find the hidden flag he left behind.

## The Challenge
The flag is hidden in the **metadata** of this image:

    https://www.gstatic.com/webp/gallery/1.webp

Download the image and inspect its EXIF/metadata carefully.

*(For your actual deployment: generate a custom image with ExifTool
and embed the flag in a metadata field like `Artist` or `Comment`.)*

## How to generate the challenge image:
Install ExifTool, then run:
    exiftool -Comment="CTF{0s1nt_k4k4r0t_f0und}" -Artist="kakarot_saiyan" challenge.jpg

## Solution
    exiftool challenge.jpg
    # Look for Comment or Artist field
    # Flag: CTF{0s1nt_k4k4r0t_f0und}

## Hints
1. Always check file metadata — images carry hidden information
2. Try: `exiftool`, `strings`, or `identify -verbose` on the image
3. The flag is in one of the standard EXIF fields