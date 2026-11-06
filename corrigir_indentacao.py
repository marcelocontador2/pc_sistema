arq = r"pc_backend\main.py"
with open(arq, "r", encoding="utf-8") as f:
    linhas = f.readlines()

# Encontra o índice da linha do Superávit Financeiro
indice_sf = -1
for i, l in enumerate(linhas):
    if 'linha("Superávit Financeiro"' in l:
        indice_sf = i
        break

if indice_sf == -1:
    print("[ERRO] Não encontrei a linha do Superávit.")
    raise SystemExit

# Pega a indentação da linha anterior (TOTAL DO PASSIVO)
indentacao_correta = ""
for j in range(indice_sf - 1, -1, -1):
    if 'linha("TOTAL DO PASSIVO"' in linhas[j]:
        indentacao_correta = linhas[j][:len(linhas[j]) - len(linhas[j].lstrip())]
        break

if not indentacao_correta:
    # Fallback: usar 8 espaços (padrão de indentação do bloco)
    indentacao_correta = "        "

# Substitui a linha com a indentação correta
linhas[indice_sf] = indentacao_correta + 'linha("Superávit Financeiro", 63825301.60, 114355899.33)\n'

with open(arq, "w", encoding="utf-8") as f:
    f.writelines(linhas)

print(f"[OK] Indentação corrigida! A linha agora tem {len(indentacao_correta)} espaços de recuo.")
