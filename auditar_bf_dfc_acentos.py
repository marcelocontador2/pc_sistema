import os, re

print("=" * 70)
print("AUDITORIA: BF (balanco_financeiro.py)")
print("=" * 70)
with open("pc_backend/app/routers/balanco_financeiro.py", "r", encoding="utf-8") as f:
    codigo_bf = f.read()

# Procura por possíveis conversões para ASCII
padroes = ["encode(", "ascii", "unidecode", "unicodedata", ".replace(", "strip("]
for p in padroes:
    ocorrencias = [(codigo_bf[:m.start()].count("\n") + 1, m.group(0)) for m in re.finditer(re.escape(p), codigo_bf)]
    if ocorrencias:
        print(f"\n  Padrão '{p}':")
        for linha, txt in ocorrencias[:5]:
            print(f"    Linha {linha}: {txt}")

# Mostra trecho de processamento
print("\n  --- Trecho do processar_bf (primeiras 80 linhas) ---")
for i, linha in enumerate(codigo_bf.split("\n")[:80], 1):
    print(f"  {i:3}: {linha}")

print("\n" + "=" * 70)
print("AUDITORIA: DFC (dfc.py)")
print("=" * 70)
with open("pc_backend/app/routers/dfc.py", "r", encoding="utf-8") as f:
    codigo_dfc = f.read()

for p in padroes:
    ocorrencias = [(codigo_dfc[:m.start()].count("\n") + 1, m.group(0)) for m in re.finditer(re.escape(p), codigo_dfc)]
    if ocorrencias:
        print(f"\n  Padrão '{p}':")
        for linha, txt in ocorrencias[:5]:
            print(f"    Linha {linha}: {txt}")

print("\n  --- Trecho da api_analise_dfc (primeiras 80 linhas) ---")
for i, linha in enumerate(codigo_dfc.split("\n")[:80], 1):
    print(f"  {i:3}: {linha}")
