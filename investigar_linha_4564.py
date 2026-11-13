import os

caminho = "pc_backend/main.py"

with open(caminho, "r", encoding="utf-8") as f:
    linhas = f.readlines()

print("=" * 80)
print("🔍 Investigando a linha 4564 (índice 4563):")
print("=" * 80)

# Mostra o contexto das linhas ao redor (10 antes e 10 depois)
inicio = max(0, 4563 - 10)
fim = min(len(linhas), 4563 + 10)

for i in range(inicio, fim):
    marcador = ">>>" if i == 4563 else "   "
    print(f"{marcador} {i+1:5d}: {linhas[i]}", end="")

print("\n" + "=" * 80)
print("🔍 Buscando TODAS as ocorrências de '{tipo}' no arquivo:")
print("=" * 80)
for i, linha in enumerate(linhas):
    if "{tipo}" in linha and "-{tipo}" in linha:
        print(f"   {i+1:5d}: {linha}", end="")

print("\n" + "=" * 80)
print("🔍 Buscando possíveis strings não fechadas próximas à linha 4564:")
print("=" * 80)
for i in range(inicio, fim):
    linha = linhas[i]
    # Conta aspas duplas e simples
    aspas_duplas = linha.count('"')
    aspas_simples = linha.count("'")
    if aspas_duplas % 2 != 0 or aspas_simples % 2 != 0:
        print(f"   ⚠️ Linha {i+1} tem aspas desbalanceadas:")
        print(f"      Aspas duplas: {aspas_duplas}, Aspas simples: {aspas_simples}")
        print(f"      Conteúdo: {linha}", end="")
        print()
