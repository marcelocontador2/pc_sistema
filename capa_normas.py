import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\relatorio_consolidado_template.html"
backup = f"pc_frontend/relatorio_consolidado_template.html.bak_capa_normas_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# Dicionário com as descrições (as mesmas da tela de Base Legal)
descricoes = {
    "Lei nº 4.320/1964": "Normas gerais de direito financeiro para elaboração e controle dos orçamentos e balanços.",
    "Resolução Cofen nº 814/2026": "Limites de despesa com pessoal e governança corporativa.",
    "Resolução Cofen nº 799/2025": "Diretrizes para gestão de riscos e controles internos.",
    "Manual de Contabilidade Aplicada ao Setor Público (MCASP)": "Diretrizes técnicas para o registro contábil no setor público.",
    "Resolução COFEN nº 340/2008 (Regulamento da Administração Financeira e Contábil)": "Regulamento da Administração Financeira e Contábil do COFEN.",
    "Resolução COFEN nº 764/2024 (Prestação de Contas)": "Processo de prestação de contas anual no Sistema Cofen/Conselhos Regionais.",
    "Normas Brasileiras de Contabilidade – Setor Público (NBC TSP)": "Normas técnicas para transparência e comparabilidade.",
    "Resolução COFEN nº 814, de 20 de agosto de 2026 (Limites de Despesa com Pessoal e Governança)": "Parâmetros de governança para despesas com pessoal."
}

# Itera e adiciona as descrições no HTML da capa
for norma, descricao in descricoes.items():
    # Procura o texto da norma na capa e adiciona a descrição ao lado (em itálico/cinza)
    # A capa do consolidado geralmente lista as normas em uma div com class "legislacao" ou similar
    if norma in html:
        # Tenta adicionar a descrição em uma tag <span> menor
        html = html.replace(norma, f"{norma} <span style='font-size:9px; color:#666; font-style:italic;'>({descricao})</span>", 1)

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Descrições adicionadas à capa do Relatório Consolidado.")
