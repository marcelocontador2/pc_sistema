import re

c = open('relatorio_final.html', encoding='utf-8-sig').read()

# 1. Remove o CSS de impressão antigo
c = re.sub(r'@media print \{.*?\n        \}', '', c, flags=re.DOTALL)

# 2. Adiciona novo CSS de impressão com margens corretas
css_print = """
        @media print {
            @page {
                size: A4;
                margin: 10mm 10mm 10mm 10mm;
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
                min-height: 270mm !important; /* Garante que a capa ocupe a página */
                display: flex !important;
                justify-content: center !important;
                padding: 40px !important;
            }
            .cover::before {
                height: 40px !important;
            }
            .cover h1 {
                font-size: 38px !important;
                margin-top: 80px !important;
            }
            .cover .total-box .value {
                font-size: 28px !important;
            }
            .section-title {
                font-size: 20px !important;
                margin-bottom: 10px !important;
            }
            .cards-grid {
                gap: 8px !important;
            }
            .card {
                padding: 12px !important;
            }
            .card .card-value {
                font-size: 18px !important;
            }
            table {
                font-size: 10px !important;
            }
            th, td {
                padding: 5px 8px !important;
            }
            .chart-container {
                flex-direction: column !important;
                gap: 10px !important;
            }
            .chart-box, .donut-container {
                max-width: 100% !important;
            }
            canvas {
                display: none !important; /* Esconde os canvas na impressão */
            }
            .canvas-img {
                display: block !important;
                max-width: 100% !important;
                height: auto !important;
            }
            .btn-salvar {
                display: none !important;
            }
            .leitura-box {
                padding: 10px !important;
                font-size: 10px !important;
            }
        }
"""

# Adiciona o CSS de impressão
c = c.replace('</style>', css_print + '\n    </style>')

# 3. Substitui a função do botão de imprimir para converter canvases em imagens
botao_antigo = '<button class="btn-salvar" onclick="window.print()">📄 Imprimir / Salvar PDF</button>'
botao_novo = '<button class="btn-salvar" onclick="prepararImpressao()">📄 Imprimir / Salvar PDF</button>'
c = c.replace(botao_antigo, botao_novo)

# 4. Adiciona a função prepararImpressao() no JavaScript
if 'function prepararImpressao' not in c:
    script = """
        function prepararImpressao() {
            // Converte cada canvas em uma imagem (para não corromper na impressão)
            const canvases = document.querySelectorAll('canvas');
            const imagensAntigas = document.querySelectorAll('.canvas-img');
            
            // Remove imagens antigas se existirem
            imagensAntigas.forEach(img => img.remove());
            
            canvases.forEach(canvas => {
                // Cria uma imagem com o conteúdo do canvas
                const img = document.createElement('img');
                img.src = canvas.toDataURL('image/png');
                img.className = 'canvas-img';
                img.style.cssText = 'display: block; max-width: 100%; height: auto; margin: 0 auto;';
                img.style.maxHeight = '280px';
                
                // Insere a imagem após o canvas
                canvas.parentNode.insertBefore(img, canvas.nextSibling);
            });
            
            // Chama a impressão
            window.print();
            
            // Após a impressão, remove as imagens (para não duplicar na tela)
            setTimeout(() => {
                document.querySelectorAll('.canvas-img').forEach(img => img.remove());
            }, 1000);
        }
    """
    pos = c.rfind('</script>')
    if pos != -1:
        c = c[:pos] + script + "\n" + c[pos:]

open('relatorio_final.html', 'w', encoding='utf-8').write(c)
print("[OK] CSS de impressão ajustado e conversão de canvas para imagem implementada!")
