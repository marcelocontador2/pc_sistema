import shutil
from datetime import datetime

ARQ = r"pc_frontend\base_legal.html"
backup = f"pc_frontend/base_legal.html.bak_descricao_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# Descrições das normas
descricoes = {
    "Lei nº 4.320/1964": "Normas gerais de direito financeiro para elaboração e controle dos orçamentos e balanços da União, Estados, Municípios e Distrito Federal.",
    "Resolução Cofen nº 814/2026": "Dispõe sobre os limites de despesa com pessoal e governança corporativa no âmbito do Sistema Cofen/Conselhos Regionais.",
    "Resolução Cofen nº 799/2025": "Estabelece diretrizes para a gestão de riscos e controles internos administrativos.",
    "Manual de Contabilidade Aplicada ao Setor Público (MCASP)": "Diretrizes técnicas para o registro contábil e a elaboração das demonstrações contábeis no setor público.",
    "Resolução COFEN nº 340/2008 (Regulamento da Administração Financeira e Contábil)": "Aprova o Regulamento da Administração Financeira e Contábil do Conselho Federal de Enfermagem.",
    "Resolução COFEN nº 764/2024 (Prestação de Contas)": "Regulamenta o processo de prestação de contas anual no âmbito do Sistema Cofen/Conselhos Regionais.",
    "Normas Brasileiras de Contabilidade – Setor Público (NBC TSP)": "Conjunto de normas técnicas que orientam a contabilidade aplicada ao setor público, visando a transparência e a comparabilidade.",
    "Resolução COFEN nº 814, de 20 de agosto de 2026 (Limites de Despesa com Pessoal e Governança)": "Estabelece limites e parâmetros de governança para as despesas com pessoal no Sistema Cofen/Conselhos Regionais."
}

for norma, descricao in descricoes.items():
    # Substitui apenas se a descrição ainda não estiver no HTML
    if descricao not in html:
        # Tenta encontrar o texto da norma e adicionar a descrição ao lado
        # Usa a abordagem de substituir a primeira ocorrência
        pos = html.find(norma)
        if pos != -1:
            # Encontra o fechamento da tag </li> mais próximo após a norma
            fim_li = html.find("</li>", pos)
            if fim_li != -1:
                # Insere a descrição antes do </li>
                html = html[:fim_li] + f"<br><span style='font-size:12px; color:#666;'>{descricao}</span>" + html[fim_li:]

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Descrições adicionadas (sem duplicação).")
