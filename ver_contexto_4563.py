caminho = "pc_backend/main.py"
with open(caminho, "r", encoding="utf-8") as f:
    linhas = f.readlines()

print("=" * 80)
print("🔍 Contexto das linhas 4555 a 4570:")
print("=" * 80)
inicio = max(0, 4555 - 1)
fim = min(len(linhas), 4570)
for i in range(inicio, fim):
    marcador = ">>>" if i == 4562 else "   "
    print(f"{marcador} {i+1:5d}: {linhas[i]}", end="")
print("=" * 80)
