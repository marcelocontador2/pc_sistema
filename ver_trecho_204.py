c = open("pc_frontend/liquidez.html", encoding="utf-8", errors="ignore").read()
linhas = c.split("\n")

print("=" * 70)
print("TRECHO DAS LINHAS 195-220 (onde esta o addEventListener)")
print("=" * 70)
for i in range(194, min(220, len(linhas))):
    print(f"  {i+1}: {linhas[i]}")
