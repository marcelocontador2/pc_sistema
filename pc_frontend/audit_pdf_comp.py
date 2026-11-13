import re

with open("composicao_receitas_despesas.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. BOTAO GERAR PDF ===")
btn = re.search(r'<button[^>]*>([^<]*Gerar PDF[^<]*)</button>', s)
if btn:
    print(btn.group(0))
else:
    print("Botao 'Gerar PDF' nao encontrado.")

print("\n=== 2. FUNCAO gerarPDF() ===")
match = re.search(r'function\s+gerarPDF\(\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
if match:
    print(match.group(0)[:1000])
else:
    print("Funcao gerarPDF() nao encontrada.")
