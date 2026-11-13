import re

with open("composicao_receitas_despesas.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. BOTÃO EXIBIR ===")
btn = re.search(r'<button[^>]*>([^<]*Exibir[^<]*)</button>', s)
if btn:
    print(btn.group(0))
else:
    print("Botao 'Exibir' nao encontrado.")

print("\n=== 2. FUNÇÃO exibirSelecionado ===")
match = re.search(r'function\s+exibirSelecionado\(\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
if match:
    print(match.group(0)[:2500])
else:
    print("Funcao nao encontrada.")

print("\n=== 3. ROTAS FETCH NA FUNÇÃO exibirSelecionado ===")
if match:
    fetches = re.findall(r'fetch\([\'"`]([^\'"`]+)[\'"`]\)', match.group(0))
    for f in fetches:
        print(f"  - {f}")
