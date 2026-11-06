import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_comparativo_receitas_v2.html"

shutil.copy2(arquivo, f"{arquivo}.bak_layout_final_{ts}")
c = open(arquivo, encoding='utf-8').read()

# Remove CSS de impressão antigos para não conflitar
c = re.sub(r'<style[^>]*id=["\']fix-print-layout["\'][^>]*>.*?</style>', '', c, flags=re.DOTALL)
c = re.sub(r'@media print\s*\{.*?\}\s*</style>', '</style>', c, flags=re.DOTALL) # Remove blocos de print antigos

# O CSS DEFINITIVO para impressão
css_fix = """
<style id="fix-print-layout">
    @media print {
        /* Força layout de bloco (tudo em coluna única) */
        .grupos-grid, .row-2col, .kpi-grid, .col-half {
            display: block !important;
            width: 100% !important;
            float: none !important;
            page-break-inside: avoid !important;
        }

        /* Containers de gráficos: tamanho fixo e esconde o que vazar */
        .chart-container {
            width: 100% !important;
            height: 220px !important;
            max-height: 220px !important;
            margin-bottom: 20px !important;
            position: relative !important;
            overflow: hidden !important; /* Impede o gráfico de invadir os cards */
            page-break-inside: avoid !important;
        }

        /* A imagem gerada pelo Playwright deve caber perfeitamente no container */
        .chart-container img, .chart-container canvas {
            max-width: 100% !important;
            max-height: 100% !important;
            object-fit: contain !important;
            display: block !important;
            margin: 0 auto !important;
        }

        /* Cards: fundo branco sólido para não misturar com gráficos */
        .grupo-card, .kpi-card {
            background-color: #ffffff !important;
            border: 1px solid #cbd5e0 !important;
            margin-bottom: 15px !important;
            padding: 15px !important;
            display: block !important;
            width: 100% !important;
            box-shadow: none !important;
            page-break-inside: avoid !important;
        }

        /* Tabelas: certificar que ficam isoladas */
        table {
            display: table !important;
            width: 100% !important;
            page-break-inside: avoid !important;
            background-color: #ffffff !important;
        }

        /* Quebra de página forçada antes de cada título H2 (exceto o da capa) */
        h2 {
            page-break-before: always !important;
            page-break-after: avoid !important;
        }
        .page-content:first-child h2 {
            page-break-before: auto !important;
        }

        /* Esconde elementos de UI */
        .btn, .no-print, i, .fa, .material-icons { display: none !important; }
    }
</style>
"""

# Adiciona o CSS no final do <head>
if '</head>' in c:
    c = c.replace('</head>', css_fix + '\n</head>', 1)
else:
    c += css_fix

# Força o container dos gráficos a ter a classe correta se não tiver
# (Alguns gráficos podem ter sido criados com div style inline)
c = c.replace('<div style="width: 100%; height: 200px; position: relative;">', '<div class="chart-container">')
c = c.replace('<div style="height: 200px;">', '<div class="chart-container">')
c = c.replace('<div style="height: 220px;">', '<div class="chart-container">')

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] CSS de impressão 'à prova de balas' injetado!")
print("-> Gráficos não vazam mais sobre os cards (overflow: hidden).")
print("-> Cards têm fundo branco sólido e são empilhados um por um.")
print("-> Tabelas isoladas e não sobrepostas.")
print("-> Páginas quebradas corretamente antes de cada seção.")
