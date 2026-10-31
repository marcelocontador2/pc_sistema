from pathlib import Path
import ast

arquivo = Path("main.py")
conteudo = arquivo.read_text(encoding="utf-8")

# Achar o trecho exato do return
trecho_antigo = '''        "custo_atual": custo_atual,'''

trecho_novo = '''        "custo_atual": custo_atual,
        "limite_pct": 0.6 if entidade.upper() == "COREN" else 0.5,
        "limite_atual": rcl_atual * (0.6 if entidade.upper() == "COREN" else 0.5),
        "limite_anterior": rcl_anterior * (0.6 if entidade.upper() == "COREN" else 0.5),
        "margem_disponivel_atual": (rcl_atual * (0.6 if entidade.upper() == "COREN" else 0.5)) - custo_atual,
        "margem_disponivel_anterior": (rcl_anterior * (0.6 if entidade.upper() == "COREN" else 0.5)) - custo_anterior,
        "entidade": entidade.upper(),'''

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo, 1)
    print("OK: Backend atualizado com limite e margem!")
else:
    print("AVISO: nao achei o trecho exato do return. Tentando variacao...")
    # Tentar com espacos diferentes
    import re
    padrao = r'(\s*)"custo_atual":\s*custo_atual,'
    match = re.search(padrao, conteudo)
    if match:
        indent = match.group(1)
        conteudo = re.sub(padrao, f'{indent}"custo_atual": custo_atual,\n{indent}"limite_pct": 0.6 if entidade.upper() == "COREN" else 0.5,\n{indent}"limite_atual": rcl_atual * (0.6 if entidade.upper() == "COREN" else 0.5),\n{indent}"limite_anterior": rcl_anterior * (0.6 if entidade.upper() == "COREN" else 0.5),\n{indent}"margem_disponivel_atual": (rcl_atual * (0.6 if entidade.upper() == "COREN" else 0.5)) - custo_atual,\n{indent}"margem_disponivel_anterior": (rcl_anterior * (0.6 if entidade.upper() == "COREN" else 0.5)) - custo_anterior,\n{indent}"entidade": entidade.upper(),', conteudo, count=1)
        print("OK: Backend atualizado (via regex)!")
    else:
        print("ERRO: nao achei o trecho do return de forma alguma.")

arquivo.write_text(conteudo, encoding="utf-8")

try:
    ast.parse(conteudo)
    print("Sintaxe OK!")
except SyntaxError as e:
    print(f"ERRO de sintaxe: {e}")
