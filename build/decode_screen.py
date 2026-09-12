from PIL import Image
import sys
from pathlib import Path

raw_file = Path("C:/mitraOS/build/vm_screen.png")
out_file = Path("C:/mitraOS/build/real_screen.png")

if not raw_file.exists():
    print("Raw file does not exist")
    sys.exit(1)

raw = raw_file.read_bytes()
print(f"Header: {raw[:8].hex()}, Total length: {len(raw)}")
payload = raw[4:] if len(raw) == 960004 else raw

if len(payload) >= 960000:
    img = Image.new("RGB", (800, 600))
    pixels = []
    for i in range(0, 960000, 2):
        val = payload[i] | (payload[i+1] << 8)
        r = ((val >> 11) & 0x1F) * 255 // 31
        g = ((val >> 5) & 0x3F) * 255 // 63
        b = (val & 0x1F) * 255 // 31
        pixels.append((r, g, b))
    img.putdata(pixels)
    img.save(out_file)
    print(f"Successfully saved {out_file} ({img.size})")
else:
    print(f"Payload too short: {len(payload)}")
