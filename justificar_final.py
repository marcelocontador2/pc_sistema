import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\relatorio_consolidado_template.html"
backup = f"pc_frontend/relatorio_consolidado_template.html.bak_justify_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# Encontra o bloco que contém "Lei nº 4.320/1964" e adiciona o style="text-align: justify;"
# A estratégia é encontrar a tag de abertura (div, p, etc.) que vem antes do texto
padrao = r'(<(?:div|p|span)[^>]*>)(\s*Lei nº 4\.320/1964)'
match = re.search(padrao, html)

if match:
    tag_abertura = match.group(1)
    texto = match.group(2)
    
    # Se a tag já tiver style, adiciona o text-align
    if 'style="' in tag_abertura:
        nova_tag = tag_abertura.replace('style="', 'style="text-align: justify; ')
    else:
        # Se não tiver style, adiciona um novo atributo
        nova_tag = tag_abertura.replace('>', ' style="text-align: justify;">')
    
    html = html.replace(tag_abertura + texto, nova_tag + texto)
    print("[OK] Justificação aplicada ao bloco da legislação.")
else:
    print("[AVISO] Não foi possível localizar o bloco da legislação. Tentando abordagem alternativa...")
    # Abordagem alternativa: procura "LEGISLAÇÃO E NORMAS APLICADAS:" e adiciona style na próxima div
    html = html.replace(
        'LEGISLAÇÃO E NORMAS APLICADAS:',
        'LEGISLAÇÃO E NORMAS APLICADAS:'
    )
    # Adiciona style em todas as divs que contenham "Lei nº"
    html = re.sub(
        r'<div([^>]*)>(\s*Lei nº 4\.320/1964)',
        r'<div\1 style="text-align: justify;">\2',
        html
    )
    print("[OK] Tentativa alternativa de justificação aplicada.")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
