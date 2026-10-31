c = open('main.py', encoding='utf-8-sig').read()

# O bloco que vamos injetar ANTES do return da API
calculo_faixas = """
        # Lógica de Faixas de Controle (Art. 6º da Resolução Cofen 814/2026)
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
        else: # COFEN
            if pct_custo_total > 50:
                faixa, cor = "Faixa Crítica (> 50%)", "danger"
            elif pct_custo_total >= 47.5:
                faixa, cor = "Faixa Prudencial (47,5% a 50%)", "warning"
            elif pct_custo_total >= 45:
                faixa, cor = "Faixa de Alerta (45% a 47,5%)", "warning"
            else:
                faixa, cor = "Abaixo da Faixa de Alerta (Saudável)", "success"

        return {
            "rcl_atual": rcl_atual,
            "rcl_anterior": rcl_anterior,
            "rcl_total": rcl_atual + rcl_anterior,
            "custo_atual": custo_atual,
            "custo_anterior": custo_anterior,
            "custo_total": custo_atual + custo_anterior,
            "limite_pct": 0.6 if entidade.upper() == "COREN" else 0.5,
            "limite_total": (rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5),
            "margem_disponivel_total": ((rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5)) - (custo_atual + custo_anterior),
            "limite_atual": (rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5),
            "limite_anterior": rcl_anterior * (0.6 if entidade.upper() == "COREN" else 0.5),
            "margem_disponivel_atual": ((rcl_atual + rcl_anterior) * (0.6 if entidade.upper() == "COREN" else 0.5)) - (custo_atual + custo_anterior),
            "margem_disponivel_anterior": (rcl_anterior * (0.6 if entidade.upper() == "COREN" else 0.5)) - custo_anterior,
            "entidade": entidade.upper(),
            "faixa_controle": faixa,
            "faixa_cor": cor,
            "pct_custo_total": pct_custo_total
        }
"""

# Encontra o trecho do return atual e o substitui pela versão com as faixas
import re
pattern = r'return \{\s*"rcl_atual": rcl_atual,\s*"rcl_anterior": rcl_anterior,.*?\}'

if re.search(pattern, c, re.DOTALL):
    c = re.sub(pattern, calculo_faixas.strip(), c, flags=re.DOTALL)
    print("[OK] Regra de negócio das Faixas de Controle injetada no main.py!")
else:
    print("[AVISO] Não foi possível encontrar o bloco exato do return para substituir.")

open('main.py', 'w', encoding='utf-8').write(c)
