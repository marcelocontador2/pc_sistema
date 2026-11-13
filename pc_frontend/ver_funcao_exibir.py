import re

with open("composicao_receitas_despesas.html", "r", encoding="utf-8") as f:
    html = f.read()

print("=== FUNÇÃO exibirSelecionado NO ARQUIVO ===")
padrao = re.compile(r'(async\s+)?function exibirSelecionado\([^)]*\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match = padrao.search(html)

if match:
    print(match.group(0))
else:
    print("  -> FUNÇÃO NÃO ENCONTRADA!")

print("\n=== BOTÃO EXIBIR NO HTML ===")
for m in re.finditer(r'<button[^>]*onclick="([^"]*)"[^>]*>([^<]*)</button>', html):
    if 'Exibir' in m.group(2) or 'exibir' in m.group(1).lower():
        print(f"  Botão: {m.group(2).strip()}")
        print(f"  onclick: {m.group(1)}")
