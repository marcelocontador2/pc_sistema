caminho = "pc_backend/main.py"
with open(caminho, "r", encoding="utf-8") as f:
    linhas = f.readlines()

print("=" * 80)
print("🔍 Contexto da linha 2089 (índice 2088):")
print("=" * 80)
inicio = max(0, 2080 - 1)
fim = min(len(linhas), 2095)
for i in range(inicio, fim):
    marcador = ">>>" if i == 2088 else "   "
    print(f"{marcador} {i+1:5d}: {linhas[i]}", end="")
print("=" * 80)
