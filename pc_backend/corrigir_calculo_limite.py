from pathlib import Path
import ast

arquivo = Path("main.py")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Corrigir o calculo do limite no retorno da api_custo_pessoal
trecho_antigo = '''        "limite_pct": 0.6 if entidade.upper() == "COREN" else 0.5,
        "limite_atual": rcl_atual * (0.6 if entidade.upper() == "COREN" else 0.5),
        "limite_anterior": rcl_anterior * (0.6 if entidade.upper() == "COREN" else 0.5),
        "margem_disponivel_atual": (rcl_atual * (0.6 if entidade.upper() == "COREN" else 0.5)) - custo_atual,
        "margem_disponivel_anterior": (rcl_anterior * (0.6 if entidade.upper() == "COREN" else 0.5)) - custo_anterior,
        "entidade": entidade.upper(),'''

trecho_novo = '''        "limite_pct": 0.6 if entidade.upper() == "COREN" else 0.5,
        "limite_total": rcl_total * (0.6 if entidade.upper() == "COREN" else 0.5),
        "margem_disponivel_total": (rcl_total * (0.6 if entidade.upper() == "COREN" else 0.5)) - custo_total,
        "limite_atual": rcl_total * (0.6 if entidade.upper() == "COREN" else 0.5),
        "limite_anterior": rcl_anterior * (0.6 if entidade.upper() == "COREN" else 0.5),
        "margem_disponivel_atual": (rcl_total * (0.6 if entidade.upper() == "COREN" else 0.5)) - custo_total,
        "margem_disponivel_anterior": (rcl_anterior * (0.6 if entidade.upper() == "COREN" else 0.5)) - custo_anterior,
        "entidade": entidade.upper(),'''

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo, 1)
    print("OK: Calculo do limite corrigido (usa rcl_total)!")
else:
    print("AVISO: nao achei o trecho exato. Tentando variacao...")
    # Tentar encontrar a linha do "limite_atual": rcl_atual *
    import re
    padrao = r'"limite_atual":\s*rcl_atual\s*\*\s*\(0\.6 if entidade\.upper\(\) == "COREN" else 0\.5\),'
    match = re.search(padrao, conteudo)
    if match:
        # Substituir apenas essa linha
        conteudo = conteudo.replace(match.group(0), '"limite_atual": rcl_total * (0.6 if entidade.upper() == "COREN" else 0.5),')
        print("OK: limite_atual corrigido via regex!")
    else:
        print("ERRO: nao consegui encontrar o calculo do limite")

arquivo.write_text(conteudo, encoding="utf-8")

try:
    ast.parse(conteudo)
    print("Sintaxe OK!")
except SyntaxError as e:
    print(f"ERRO de sintaxe: {e}")
