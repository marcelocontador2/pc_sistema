import shutil
from datetime import datetime

ARQ = r"pc_frontend\relatorio_consolidado_template.html"
backup = f"pc_frontend/relatorio_consolidado_template.html.bak_css_justify_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# Adiciona uma regra CSS no <head> que justifica o bloco de legislação
# A regra atinge qualquer elemento que contenha a classe "legislacao" ou que esteja próximo ao título
css_justify = """
<style>
/* Força a justificação do texto da legislação */
.legislacao, .legislacao p, div[id*="legislacao"], .capa-legislacao {
    text-align: justify !important;
    text-justify: inter-word !important;
}
/* Caso o texto esteja solto em um parágrafo após o título */
h3 + p, h2 + p, .titulo-secao + p {
    text-align: justify !important;
}
</style>
"""

# Insere o CSS antes do fechamento do </head>
if "</head>" in html:
    html = html.replace("</head>", css_justify + "</head>")
    print("[OK] CSS de justificação adicionado ao <head>.")
else:
    # Se não houver <head>, insere no início do <body>
    html = html.replace("<body>", "<body>" + css_justify)
    print("[OK] CSS de justificação adicionado ao <body>.")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
