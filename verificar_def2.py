import ast, re

c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

# Encontra todas as definicoes de "def buscar("
ocorrencias = [(m.start(), m.group()) for m in re.finditer(r'def buscar\([^)]+\):', c)]
print(f"[INFO] Encontradas {len(ocorrencias)} definicoes de 'buscar'.\n")

# Verifica qual e a versao corrigida (com col_espec in [0, 3])
for idx, match in ocorrencias:
    fim = c.find('\n    def ', idx + 10)
    if fim == -1:
        fim = c.find('\ndef ', idx + 10)
    if fim == -1:
        fim = idx + 800
    bloco = c[idx:fim]
    if 'col_espec in [0, 3]' in bloco:
        print(f"[OK] Definicao corrigida encontrada em: {match}")
        print(f"  Posicao: {idx}")
        # Mostra as primeiras linhas
        print(f"  Primeiras linhas:")
        for ln in bloco.split("\n")[:8]:
            print(f"    {ln}")
        print()

# Verifica as chamadas para "TOTAL DO PASSIVO" no contexto da conferencia
print("=" * 70)
print("CHAMADAS PARA 'TOTAL DO PASSIVO' NO CONTEXTO DA CONFERENCIA")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if 'buscar(' in ln and 'PASSIVO' in ln.upper() and 'TOTAL' in ln.upper():
        print(f"  Linha {i}: {ln.strip()[:150]}")
