import re

c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

print("=" * 70)
print("DIAGNÓSTICO: ROTA /gerar_pdf_comparativo_receitas")
print("=" * 70)

# Encontra a função
match = re.search(r'(@app\.get\("/gerar_pdf_comparativo_receitas"\).*?)(?=\n@app\.|\Z)', c, re.DOTALL)

if match:
    codigo = match.group(1)
    print("\n--- CÓDIGO ATUAL DA ROTA ---")
    print(codigo[:2000])
else:
    print("[ERRO] Rota não encontrada.")
