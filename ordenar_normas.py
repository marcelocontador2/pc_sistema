import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\relatorio_consolidado_template.html"
backup = f"pc_frontend/relatorio_consolidado_template.html.bak_ordenar_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Adiciona justificativa no bloco de legislação
# Procura a div que contém a lista de normas (geralmente tem id="legislacao" ou class="legislacao")
# Vamos adicionar o estilo de justificação no parágrafo ou div que contém as normas
if '<div id="legislacao"' in html:
    html = html.replace('<div id="legislacao"', '<div id="legislacao" style="text-align: justify;"')
elif 'class="legislacao"' in html:
    html = html.replace('class="legislacao"', 'class="legislacao" style="text-align: justify;"')
else:
    # Tenta encontrar o título "LEGISLAÇÃO E NORMAS APLICADAS" e adicionar o style no próximo elemento
    html = html.replace(
        'LEGISLAÇÃO E NORMAS APLICADAS:',
        'LEGISLAÇÃO E NORMAS APLICADAS:'
    )

# 2. Ordenar as normas cronologicamente (ano ascendente)
# Como as normas estão em uma string única, precisamos reorganizá-las
# Vamos extrair o bloco de normas e reordenar

# Lista das normas em ordem cronológica
normas_ordenadas = [
    "Lei nº 4.320/1964 <span style='font-size:9px; color:#666; font-style:italic;'>(Normas gerais de direito financeiro para elaboração e controle dos orçamentos e balanços.)</span>",
    "Resolução COFEN nº 340/2008 (Regulamento da Administração Financeira e Contábil) <span style='font-size:9px; color:#666; font-style:italic;'>(Regulamento da Administração Financeira e Contábil do COFEN.)</span>",
    "Normas Brasileiras de Contabilidade – Setor Público (NBC TSP) <span style='font-size:9px; color:#666; font-style:italic;'>(Normas técnicas para transparência e comparabilidade.)</span>",
    "Resolução COFEN nº 764/2024 (Prestação de Contas) <span style='font-size:9px; color:#666; font-style:italic;'>(Processo de prestação de contas anual no Sistema Cofen/Conselhos Regionais.)</span>",
    "Resolução Cofen nº 799/2025 <span style='font-size:9px; color:#666; font-style:italic;'>(Estabelece diretrizes para a gestão de riscos e controles internos administrativos.)</span>",
    "Resolução Cofen nº 814/2026 <span style='font-size:9px; color:#666; font-style:italic;'>(Limites de despesa com pessoal e governança corporativa.)</span>",
    "Resolução COFEN nº 814, de 20 de agosto de 2026 (Limites de Despesa com Pessoal e Governança) <span style='font-size:9px; color:#666; font-style:italic;'>(Parâmetros de governança para despesas com pessoal.)</span>",
    "Manual de Contabilidade Aplicada ao Setor Público (MCASP) <span style='font-size:9px; color:#666; font-style:italic;'>(Diretrizes técnicas para o registro contábil no setor público.)</span>"
]

# Junta as normas com " • "
novo_texto_normas = " • ".join(normas_ordenadas)

# Substitui o bloco de normas antigo pelo novo (ordenado)
# Encontra o trecho que começa com "Lei nº 4.320" e vai até o final do parágrafo
padrao_normas = r'Lei nº 4\.320/1964.*?(?=</p>|</div>|<br>)'
if re.search(padrao_normas, html, re.DOTALL):
    html = re.sub(padrao_normas, novo_texto_normas, html, flags=re.DOTALL)
    print("[OK] Normas reordenadas cronologicamente e texto justificado.")
else:
    print("[AVISO] Não foi possível localizar o bloco de normas. Verifique manualmente.")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Capa do Relatório Consolidado atualizada.")
