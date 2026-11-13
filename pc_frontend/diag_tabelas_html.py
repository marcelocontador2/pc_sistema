import re

with open("composicao_receitas_despesas.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== TRECHO DO HTML COM AS TABELAS ===")
# Procura as tabelas e mostra o contexto
for m in re.finditer(r'<table[^>]*id="tab-receitas"[^>]*>.*?</table>', s, re.DOTALL):
    print(m.group(0)[:800])
    print("---")

for m in re.finditer(r'<table[^>]*id="tab-despesas"[^>]*>.*?</table>', s, re.DOTALL):
    print(m.group(0)[:800])
    print("---")

print("\n=== TAGS TBODY ENCONTRADAS ===")
for m in re.finditer(r'<tbody[^>]*>', s):
    print(m.group(0))
