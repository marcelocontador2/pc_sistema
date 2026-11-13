import re

with open("analise_dmpl.html", "r", encoding="utf-8") as f:
    html = f.read()

print("=== FUNCAO salvar() NO FRONTEND ===")
padrao = re.compile(r'function salvar\(\)\s*\{.*?\n\s*\}', re.DOTALL)
match = padrao.search(html)
if match:
    print(match.group(0))
else:
    print("Funcao salvar() nao encontrada.")

print("\n=== BOTOES E ONCLICK ===")
for m in re.finditer(r'<button[^>]*onclick="([^"]*)"[^>]*>([^<]*)</button>', html):
    print(f"Botao '{m.group(2).strip()}' -> {m.group(1)}")

print("\n=== CARREGAR HISTORICO ===")
padrao2 = re.compile(r'function carregarHistorico\(\)\s*\{.*?\n\s*\}', re.DOTALL)
match2 = padrao2.search(html)
if match2:
    print(match2.group(0)[:300])
