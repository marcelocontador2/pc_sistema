import ast, re

c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

# Encontra todas as definicoes de "def buscar("
ocorrencias = [(m.start(), m.group()) for m in re.finditer(r'def buscar\([^)]+\):', c)]
print(f"[INFO] Encontradas {len(ocorrencias)} definicoes de 'buscar'.\n")

for i, (idx, match) in enumerate(ocorrencias):
    # Pega o bloco (ate o proximo "def" ou 1000 chars)
    fim = c.find('\n    def ', idx + 10)
    if fim == -1:
        fim = c.find('\ndef ', idx + 10)
    if fim == -1:
        fim = idx + 800
    bloco = c[idx:fim]

    # Mostra a assinatura e as primeiras linhas
    print(f"--- Definicao {i+1} (posicao {idx}) ---")
    print(f"Assinatura: {match}")
    print(f"Primeiras linhas:")
    for ln in bloco.split("\n")[:6]:
        print(f"  {ln}")
    print()

    # Verifica se e a versao corrigida
    if 'col_espec in [0, 3]' in bloco:
        print("  [OK] Esta e a versao corrigida (col_espec in [0, 3]).")
    else:
        print("  [AVISO] Esta NAO e a versao corrigida.")
    print()
