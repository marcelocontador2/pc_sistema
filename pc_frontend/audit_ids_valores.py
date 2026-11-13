import re

with open("panorama.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== TODOS OS IDs DOS VALORES ===")
ids = re.findall(r'id="(val-[^"]+)"', s)
for i in ids:
    print(f"  - {i}")
