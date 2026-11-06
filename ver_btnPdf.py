c = open("pc_frontend/liquidez.html", encoding="utf-8", errors="ignore").read()
linhas = c.split("\n")

print("=" * 70)
print("TRECHO DAS LINHAS 180-195 (onde btnPdf e definido)")
print("=" * 70)
for i in range(179, min(195, len(linhas))):
    print(f"  {i+1}: {linhas[i]}")
