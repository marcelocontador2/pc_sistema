import csv, os, re

# Reproduz EXATAMENTE a funcao _limpar_valor do integridade.py
def _limpar_valor(valor):
    if not valor: return 0.0
    v = str(valor).upper().replace("R$", "").replace(" ", "").replace("\n", "").replace("\r", "").strip()
    if not v or v == '-': return 0.0
    mult = -1.0 if v.endswith('C') else 1.0
    v = v.replace("C", "").replace("D", "")
    if ',' in v and '.' in v: v = v.replace(".", "").replace(",", ".")
    elif ',' in v: v = v.replace(",", ".")
    try: return float(v) * mult
    except: return 0.0

caminho = r"pc_storage/uploads_raw/BALANCO_PATRIMONIAL_2026_TRIMESTRE_3.csv"
linhas = []
with open(caminho, 'r', encoding='latin-1', errors='ignore') as f:
    linhas = [row for row in csv.reader(f, delimiter=';')]

print("=" * 70)
print("SIMULANDO A LEITURA DO BP (integridade.py)")
print("=" * 70)

# Simula o loop do integridade.py
for i, p in enumerate(linhas, 1):
    if len(p) >= 4:
        if p[0].strip().upper() == "TOTAL":
            print(f"\n[ENCONTRADO] Linha {i} com 'TOTAL' na coluna 0:")
            print(f"  p[0] = {repr(p[0])}")
            print(f"  p[1] = {repr(p[1])} -> _limpar_valor = {_limpar_valor(p[1])}")
            print(f"  p[2] = {repr(p[2])}")
            print(f"  p[3] = {repr(p[3])} -> _limpar_valor = {_limpar_valor(p[3])}")
            if len(p) > 4:
                print(f"  p[4] = {repr(p[4])} -> _limpar_valor = {_limpar_valor(p[4])}")
            if len(p) > 5:
                print(f"  p[5] = {repr(p[5])} -> _limpar_valor = {_limpar_valor(p[5])}")
            break

print("\n" + "=" * 70)
print("DIAGNOSTICO FINAL: O que o integridade.py VAI LER")
print("=" * 70)
ativo, passivo = 0.0, 0.0
for p in linhas:
    if len(p) >= 4:
        if p[0].strip().upper() == "TOTAL":
            ativo = _limpar_valor(p[1])
            passivo = _limpar_valor(p[3])  # ← O CÓDIGO ATUAL PEGA DA COLUNA 3
            break
print(f"  Ativo  (p[1]) = {ativo}")
print(f"  Passivo (p[3]) = {passivo}  ← ATUAL (deveria ser p[4])")
diff = ativo - passivo
print(f"  Diferenca = {diff}")
