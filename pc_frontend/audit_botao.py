import re

with open("composicao_receitas_despesas.html", "r", encoding="utf-8") as f:
    html = f.read()

print("=== TODOS OS BOTOES NO HTML ===")
for m in re.finditer(r'<button[^>]*>([^<]*)</button>', html):
    print(f"  - '{m.group(1).strip()}'")

print("\n=== FUNCAO exibirNovo NO HTML ===")
if "function exibirNovo" in html:
    print("  -> ENCONTRADA")
else:
    print("  -> NAO ENCONTRADA")

print("\n=== TRECHO ONDE O BOTAO FOI INSERIDO ===")
pos = html.find("exibirNovo")
if pos != -1:
    print(html[max(0, pos-200):pos+100])
else:
    print("  -> Texto 'exibirNovo' nao encontrado no HTML!")
