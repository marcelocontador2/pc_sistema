import re

c = open('main.py', encoding='utf-8-sig').read()

# O novo bloco com as faixas de controle
novo_bloco = '''    # Lógica de Faixas de Controle (Art. 6º da Resolução Cofen 814/2026)
    pct_custo_total = ((custo_atual + custo_anterior) / (rcl_atual + rcl_anterior)) * 100 if (rcl_atual + rcl_anterior) > 0 else 0
    is_coren = (entidade.upper() == "COREN")
    
    if is_coren:
        if pct_custo_total > 60:
            faixa, cor = "Faixa Crítica (> 60%)", "danger"
        elif pct_custo_total >= 57:
            faixa, cor = "Faixa Prudencial (57% a 60%)", "warning"
        elif pct_custo_total >= 54:
            faixa, cor = "Faixa de Alerta (54% a 57%)", "warning"
        else:
            faixa, cor = "Abaixo da Faixa de Alerta (Saudável)", "success"
    else:
        if pct_custo_total > 50:
            faixa, cor = "Faixa Crítica (> 50%)", "danger"
        elif pct_custo_total >= 47.5:
            faixa, cor = "Faixa Prudencial (47,5% a 50%)", "warning"
        elif pct_custo_total >= 45:
            faixa, cor = "Faixa de Alerta (45% a 47,5%)", "warning"
        else:
            faixa, cor = "Abaixo da Faixa de Alerta (Saudável)", "success"

    return {
        "erro": False,
        "rcl_atual": rcl_atual,
        "rcl_anterior": rcl_anterior,
        "rcl_total": rcl_atual + rcl_anterior,
        "pessoal_atual": dados_atual["pessoal"],
        "pessoal_anterior": sum(d["pessoal"] for d in dados_anteriores),
        "pessoal_total": dados_atual["pessoal"] + sum(d["pessoal"] for d in dados_anteriores),
        "outras_atual": dados_atual["outras"],
        "outras_anterior": sum(d["outras"] for d in dados_anteriores),
        "outras_total": dados_atual["outras"] + sum(d["outras"] for d in dados_anteriores),
        "terc_atual": dados_atual["terc"],
        "terc_anterior": sum(d["terc"] for d in dados_anteriores),
        "terc_total": dados_atual["terc"] + sum(d["terc"] for d in dados_anteriores),
        "custo_atual": custo_atual,
        "limite_pct": 0.6 if entidade.upper() == "COREN" else 0.5,
        "limite_total": (rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5),
        "margem_disponivel_total": ((rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5)) - (custo_atual + custo_anterior),
        "limite_atual": (rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5),
        "limite_anterior": rcl_anterior * (0.6 if entidade.upper() == "COREN" else 0.5),
        "margem_disponivel_atual": ((rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5)) - (custo_atual + custo_anterior),
        "margem_disponivel_anterior": (rcl_anterior * (0.6 if entidade.upper() == "COREN" else 0.5)) - custo_anterior,
        "entidade": entidade.upper(),
        "custo_anterior": custo_anterior,
        "custo_total": custo_atual + custo_anterior,
        "faixa_controle": faixa,
        "faixa_cor": cor,
        "pct_custo_total": pct_custo_total
    }'''

# Localizar o return da api_custo_pessoal
inicio_funcao = c.find('async def api_custo_pessoal')
if inicio_funcao == -1:
    print("[ERRO] Função api_custo_pessoal não encontrada.")
else:
    # Regex para pegar o return que tem "erro": False e "rcl_atual"
    padrao = r'    return \{\s*\n\s*"erro": False,\s*\n\s*"rcl_atual": rcl_atual,.*?\n    \}'
    match = re.search(padrao, c[inicio_funcao:], re.DOTALL)
    if match:
        inicio = inicio_funcao + match.start()
        fim = inicio_funcao + match.end()
        c = c[:inicio] + novo_bloco + c[fim:]
        print("[OK] Lógica de faixas injetada com sucesso no backend!")
    else:
        print("[ERRO] Padrão do return não encontrado.")

open('main.py', 'w', encoding='utf-8').write(c)
