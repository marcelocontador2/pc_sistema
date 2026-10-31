from pathlib import Path
import ast

arquivo = Path("main.py")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Adicionar o calculo de rcl_total e custo_total antes do return
trecho_antigo = '''        "limite_pct": 0.6 if entidade.upper() == "COREN" else 0.5,
        "limite_total": rcl_total * (0.6 if entidade.upper() == "COREN" else 0.5),'''

trecho_novo = '''        # Calcular totais (antes de usar no retorno)
        "limite_pct": 0.6 if entidade.upper() == "COREN" else 0.5,
        "limite_total": (rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5),'''

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo, 1)
    print("OK: rcl_total calculado antes do return!")
else:
    print("AVISO: nao achei o trecho exato")

# 2. Corrigir o "margem_disponivel_total" tambem
trecho_antigo2 = '''        "margem_disponivel_total": (rcl_total * (0.6 if entidade.upper() == "COREN" else 0.5)) - custo_total,'''
trecho_novo2 = '''        "margem_disponivel_total": ((rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5)) - (custo_atual + custo_anterior),'''

if trecho_antigo2 in conteudo:
    conteudo = conteudo.replace(trecho_antigo2, trecho_novo2, 1)
    print("OK: margem_disponivel_total corrigida!")

# 3. Corrigir o "limite_atual" para usar rcl_total
trecho_antigo3 = '''        "limite_atual": rcl_total * (0.6 if entidade.upper() == "COREN" else 0.5),'''
trecho_novo3 = '''        "limite_atual": (rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5),'''

if trecho_antigo3 in conteudo:
    conteudo = conteudo.replace(trecho_antigo3, trecho_novo3, 1)
    print("OK: limite_atual corrigido!")

# 4. Corrigir o "margem_disponivel_atual" para usar rcl_total
trecho_antigo4 = '''        "margem_disponivel_atual": (rcl_total * (0.6 if entidade.upper() == "COREN" else 0.5)) - custo_total,'''
trecho_novo4 = '''        "margem_disponivel_atual": ((rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5)) - (custo_atual + custo_anterior),'''

if trecho_antigo4 in conteudo:
    conteudo = conteudo.replace(trecho_antigo4, trecho_novo4, 1)
    print("OK: margem_disponivel_atual corrigida!")

arquivo.write_text(conteudo, encoding="utf-8")

try:
    ast.parse(conteudo)
    print("Sintaxe OK!")
except SyntaxError as e:
    print(f"ERRO de sintaxe: {e}")
