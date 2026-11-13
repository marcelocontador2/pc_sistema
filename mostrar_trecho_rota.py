import re

caminho = "pc_backend/main.py"

with open(caminho, "r", encoding="utf-8") as f:
    linhas = f.readlines()

rota_alvo = "/analise_comparativo_receitas"

# Encontra o número da linha onde a rota aparece
linhas_encontradas = []
for i, linha in enumerate(linhas):
    if rota_alvo in linha:
        linhas_encontradas.append(i)

if not linhas_encontradas:
    print("❌ Rota não encontrada no main.py.")
    exit()

print(f"✅ Rota encontrada nas linhas: {[l+1 for l in linhas_encontradas]}")
print("=" * 80)

# Mostra um bloco de 120 linhas a partir da primeira ocorrência
inicio = max(0, linhas_encontradas[0] - 5)
fim = min(len(linhas), linhas_encontradas[0] + 120)

for i in range(inicio, fim):
    marcador = ">>>" if i in linhas_encontradas else "   "
    print(f"{marcador} {i+1:5d}: {linhas[i]}", end="")

print("\n" + "=" * 80)
print("📋 Copie o bloco acima (da linha do @app.route até o final da função) e me envie para eu corrigir com precisão.")
