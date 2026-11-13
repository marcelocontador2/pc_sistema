import re

with open("composicao_receitas_despesas.html", "r", encoding="utf-8") as f:
    html = f.read()

print("=== IDs DAS TABELAS NO HTML ===")
for m in re.finditer(r'<table[^>]*id="([^"]+)"', html):
    print(f"  - {m.group(1)}")
if not re.search(r'<table[^>]*id="', html):
    print("  -> Nenhuma tabela tem ID!")

print("\n=== BOTÕES E ONCLICK ===")
for m in re.finditer(r'<button[^>]*onclick="([^"]*)"[^>]*>([^<]*)</button>', html):
    print(f"  - '{m.group(2).strip()}' -> {m.group(1)}")

print("\n=== FUNÇÃO exibirSelecionado (se existir) ===")
padrao = re.compile(r'(async\s+)?function exibirSelecionado\([^)]*\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match = padrao.search(html)
if match:
    print(match.group(0)[:800])
else:
    print("  -> Não encontrada.")

print("\n=== ROTAS FETCH ===")
for m in re.finditer(r"fetch\([\'\"]([^\'\"]+)", html):
    print(f"  - {m.group(1)}")
