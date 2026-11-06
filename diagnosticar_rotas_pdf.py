import re

with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

print("=== ROTAS DE GERAÇÃO DE PDF POR MÓDULO ===")
# Procura todas as rotas /gerar_pdf_* no main.py
rotas = re.findall(r'@app\.get\("(/gerar_pdf[^"]*)"\)', codigo)
for r in sorted(set(rotas)):
    print(f"  {r}")

print("\n=== ROTAS DE HISTÓRICO QUE TEMOS MAPEADAS ===")
tabelas = re.findall(r'historico_(?:analise_)?\w+', codigo)
print("  Tabelas mencionadas:", sorted(set(tabelas))[:20])
