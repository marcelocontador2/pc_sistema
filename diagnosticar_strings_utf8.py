import re

with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

# Extrai o bloco da função DFC
idx_dfc = codigo.find("def gerar_pdf_analise_dfc")
fim_dfc = codigo.find("\n@app.", idx_dfc)
bloco_dfc = codigo[idx_dfc:fim_dfc]

print("=" * 70)
print("STRINGS NA FUNÇÃO DFC")
print("=" * 70)

# Mostra todas as strings com "cell" que contenham textos
for m in re.finditer(r'pdf\.cell\([^)]*["\']([^"\']+)["\']', bloco_dfc):
    texto = m.group(1)
    # Mostra a string e seus bytes em UTF-8
    print(f"String: '{texto}'")
    print(f"Bytes UTF-8: {texto.encode('utf-8')}")
    print(f"Tem acento? {'Sim' if any(ord(c) > 127 for c in texto) else 'Não'}")
    print("-" * 40)

print("\n" + "=" * 70)
print("STRINGS NA FUNÇÃO BF")
print("=" * 70)
idx_bf = codigo.find("def gerar_pdf_analise_financeira_bf")
fim_bf = codigo.find("\n@app.", idx_bf)
bloco_bf = codigo[idx_bf:fim_bf]

for m in re.finditer(r'pdf\.cell\([^)]*["\']([^"\']+)["\']', bloco_bf):
    texto = m.group(1)
    print(f"String: '{texto}'")
    print(f"Bytes UTF-8: {texto.encode('utf-8')}")
    print(f"Tem acento? {'Sim' if any(ord(c) > 127 for c in texto) else 'Não'}")
    print("-" * 40)
