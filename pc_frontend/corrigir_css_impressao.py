import re

c = open('relatorio_final.html', encoding='utf-8-sig').read()

# Remove o CSS de impressão antigo (se existir)
c = re.sub(r'@media print \{.*?\n        \}', '', c, flags=re.DOTALL)
# Remove o @media print que está dentro do <style> (caso tenha ficado)
c = re.sub(r'@media print \{.*?\n        \}', '', c, flags=re.DOTALL)

# Adiciona o novo CSS de impressão no final do <style>
css_print = """
        /* ===== CSS ESPECÍFICO PARA IMPRESSÃO (A4) ===== */
        @media print {
            @page {
                size: A4;
                margin: 15mm 15mm 15mm 15mm;
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
                page-break-inside: avoid;
                height: auto !important;
                min-height: auto !important;
                overflow: visible !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            .page:last-child {
                page-break-after: auto;
            }
            .cover {
                min-height: 250mm; /* Aproximadamente uma página A4 */
            }
            /* Reduz tamanhos para caber */
            .section-title {
                font-size: 22px !important;
                margin-bottom: 15px !important;
            }
            .cards-grid {
                gap: 10px !important;
            }
            .card {
                padding: 15px !important;
            }
            .card .card-value {
                font-size: 20px !important;
            }
            table {
                font-size: 11px !important;
            }
            th, td {
                padding: 8px 10px !important;
            }
            .chart-container {
                flex-direction: column !important;
                gap: 20px !important;
            }
            .chart-box, .donut-container {
                max-width: 100% !important;
            }
            canvas {
                max-height: 250px !important;
            }
            .btn-salvar {
                display: none !important;
            }
            .leitura-box {
                padding: 15px !important;
                font-size: 11px !important;
            }
            .leitura-box h3 {
                font-size: 11px !important;
            }
        }
"""

# Adiciona o novo CSS antes de </style>
c = c.replace('</style>', css_print + '\n    </style>')

# Garante que a página de composição tenha a tabela ao lado do donut no print
# Mas no print, como pode não caber, vamos empilhar
css_composicao_print = """
        @media print {
            /* Composição: empilha donut e tabela se não couber */
            .page[data-page="composicao"] > div[style*="display: flex"] {
                flex-direction: column !important;
            }
        }
"""
c = c.replace('</style>', css_composicao_print + '\n    </style>')

open('relatorio_final.html', 'w', encoding='utf-8').write(c)
print("[OK] CSS de impressão ajustado para A4 com auto-ajuste!")
