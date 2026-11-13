import re

with open("composicao_receitas_despesas.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== FUNCAO gerarPDFHistorico() ===")
match = re.search(r'function\s+gerarPDFHistorico\(\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
if match:
    print(match.group(0)[:1500])
else:
    print("Funcao gerarPDFHistorico() nao encontrada.")
