import re

c = open('relatorio_final.html', encoding='utf-8-sig').read()

# 1. Remove TODO o CSS de impressão antigo (tanto @media print quanto @page)
c = re.sub(r'@media print \{.*?\n        \}', '', c, flags=re.DOTALL)
c = re.sub(r'@page \{.*?\n        \}', '', c, flags=re.DOTALL)

# 2. Adiciona o novo CSS de impressão (limpo, com margens de 1.5cm)
css_print = """
        @media print {
            @page {
                size: A4;
                margin: 15mm 15mm 15mm 15mm; /* 1.5cm de margem */
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
                width: 100% !important;
            }
            .page:last-child {
                page-break-after: auto;
            }
            .cover {
                min-height: 260mm !important;
                display: flex !important;
                justify-content: center !important;
                padding: 0 !important;
            }
            .cover::before {
                height: 40px !important;
            }
            .cover h1 {
                font-size: 32px !important;
                margin-top: 60px !important;
            }
            .section-title {
                font-size: 18px !important;
                margin-bottom: 8px !important;
            }
            .cards-grid {
                gap: 8px !important;
            }
            .card {
                padding: 10px !important;
            }
            .card .card-value {
                font-size: 16px !important;
            }
            table {
                font-size: 9px !important;
            }
            th, td {
                padding: 4px 6px !important;
            }
            /* Esconde canvas e mostra as imagens geradas */
            canvas {
                display: none !important;
            }
            .canvas-img {
                display: block !important;
                max-width: 100% !important;
                height: auto !important;
                max-height: 240px !important;
                margin: 0 auto !important;
            }
            .chart-container {
                flex-direction: column !important;
                gap: 8px !important;
            }
            .btn-salvar {
                display: none !important;
            }
            .leitura-box {
                padding: 8px !important;
                font-size: 9px !important;
            }
            .leitura-box h3 {
                font-size: 9px !important;
            }
            .leitura-box ul {
                font-size: 9px !important;
                padding-left: 15px !important;
            }
        }
"""

# Adiciona o novo CSS antes de </style>
c = c.replace('</style>', css_print + '\n    </style>')

# 3. Substitui a função de impressão por uma versão robusta
# Primeiro, remove a função antiga (se existir)
c = re.sub(r'function prepararImpressao\(\) \{.*?\n        \}', '', c, flags=re.DOTALL)

nova_funcao = """
        function prepararImpressao() {
            // Remove imagens antigas
            document.querySelectorAll('.canvas-img').forEach(img => img.remove());
            
            // Converte cada canvas em imagem
            const canvases = document.querySelectorAll('canvas');
            canvases.forEach(canvas => {
                try {
                    const img = document.createElement('img');
                    img.src = canvas.toDataURL('image/png');
                    img.className = 'canvas-img';
                    img.style.cssText = 'display: none; max-width: 100%; max-height: 240px; margin: 0 auto;';
                    canvas.parentNode.insertBefore(img, canvas.nextSibling);
                } catch (e) {
                    console.error('Erro ao converter canvas:', e);
                }
            });
            
            // Ativa a impressão
            setTimeout(() => {
                document.querySelectorAll('.canvas-img').forEach(img => {
                    img.style.display = 'block';
                });
                window.print();
                
                // Depois de imprimir, esconde as imagens e mostra os canvas novamente
                setTimeout(() => {
                    document.querySelectorAll('.canvas-img').forEach(img => img.remove());
                    document.querySelectorAll('canvas').forEach(c => c.style.display = 'block');
                }, 1000);
            }, 200);
        }
"""

# Adiciona a nova função antes do </script> final
pos = c.rfind('</script>')
if pos != -1:
    c = c[:pos] + nova_funcao + "\n" + c[pos:]

open('relatorio_final.html', 'w', encoding='utf-8').write(c)
print("[OK] CSS de impressão com margens de 1.5cm e conversão robusta de canvas!")
