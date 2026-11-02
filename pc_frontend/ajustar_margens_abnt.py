import re

c = open('relatorio_final.html', encoding='utf-8-sig').read()

# 1. Remove TODO o CSS de impressão antigo
c = re.sub(r'@media print \{.*?\n        \}', '', c, flags=re.DOTALL)
c = re.sub(r'@page \{.*?\n        \}', '', c, flags=re.DOTALL)

# 2. Adiciona o novo CSS com margens ABNT
css_print = """
        /* ===== CSS DE IMPRESSÃO - PADRÃO ABNT ===== */
        @media print {
            @page {
                size: A4;
                margin: 3cm 2cm 2cm 3cm; /* Superior 3cm, Direita 2cm, Inferior 2cm, Esquerda 3cm */
            }
            body {
                margin: 0;
                padding: 0;
                background: #fff;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            .page {
                page-break-after: always;
                page-break-inside: auto;
                height: auto !important;
                min-height: auto !important;
                overflow: visible !important;
                padding: 0 !important;
                margin: 0 !important;
                width: 100% !important;
                box-sizing: border-box !important;
            }
            .page:last-child {
                page-break-after: auto;
            }
            .cover {
                min-height: auto !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: flex-start !important;
                padding-top: 4cm !important;
                position: relative !important;
            }
            .cover::before {
                height: 40px !important;
                position: absolute !important;
                top: -3cm !important; /* Compensa a margem superior */
                left: -3cm !important;
                width: calc(100% + 5cm) !important;
            }
            .cover h1 {
                font-size: 32px !important;
                margin-top: 30px !important;
                margin-bottom: 15px !important;
            }
            .cover .subtitle {
                font-size: 14px !important;
            }
            .cover .total-box {
                margin-top: 30px !important;
            }
            .cover .total-box .value {
                font-size: 26px !important;
            }
            .section-title {
                font-size: 18px !important;
                margin-bottom: 10px !important;
                margin-top: 0 !important;
            }
            .section-subtitle {
                font-size: 10px !important;
                margin-bottom: 5px !important;
            }
            .cards-grid {
                gap: 10px !important;
                margin-bottom: 15px !important;
            }
            .card {
                padding: 12px !important;
            }
            .card .card-value {
                font-size: 18px !important;
            }
            .card .card-title {
                font-size: 10px !important;
            }
            .card .card-sub {
                font-size: 10px !important;
            }
            table {
                font-size: 10px !important;
                page-break-inside: auto !important;
            }
            th, td {
                padding: 5px 8px !important;
            }
            .table-container {
                page-break-inside: auto !important;
                max-height: none !important;
                overflow: visible !important;
            }
            .chart-container {
                flex-direction: column !important;
                gap: 10px !important;
                page-break-inside: avoid !important;
            }
            canvas {
                display: none !important;
            }
            .canvas-img {
                display: block !important;
                max-width: 100% !important;
                height: auto !important;
                max-height: 220px !important;
                margin: 0 auto !important;
            }
            .btn-salvar {
                display: none !important;
            }
            .leitura-box {
                padding: 10px !important;
                font-size: 10px !important;
                page-break-inside: avoid !important;
            }
            .leitura-box h3 {
                font-size: 10px !important;
            }
            .leitura-box ul {
                font-size: 10px !important;
                padding-left: 15px !important;
                margin: 5px 0 !important;
            }
            /* Força a quebra de página antes de cada nova seção */
            .page + .page {
                page-break-before: always !important;
            }
            /* A tabela detalhada não deve ter muito espaço vazio */
            .page[style*="Tabela Detalhada"] {
                min-height: auto !important;
            }
        }
"""

# Adiciona o novo CSS antes de </style>
c = c.replace('</style>', css_print + '\n    </style>')

open('relatorio_final.html', 'w', encoding='utf-8').write(c)
print("[OK] CSS de impressão ajustado com margens ABNT (3cm esquerda/superior, 2cm direita/inferior)!")
