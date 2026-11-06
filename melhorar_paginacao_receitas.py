import re, shutil, datetime, os

ts = datetime.datetime.now().strftime('%H%M%S')

# O arquivo correto é o _v2 que vimos nos logs anteriores
arquivo = r"pc_frontend\relatorio_comparativo_receitas_v2.html"
if not os.path.exists(arquivo):
    arquivo = r"pc_frontend\relatorio_comparativo_receitas.html"

print(f"[INFO] Ajustando: {os.path.basename(arquivo)}")

shutil.copy2(arquivo, f"{arquivo}.bak_paginacao_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Remove CSS de impressão antigo (se houver)
c = re.sub(r'<style>\s*/\*\s*REGRAS DE IMPRESSÃO.*?</style>', '', c, flags=re.DOTALL)
c = re.sub(r'<style>\s*@media print.*?</style>', '', c, flags=re.DOTALL)

# 2. Novo CSS de Paginação Profissional
css = """
<style>
    @media print {
        /* Força A4 Paisagem para caberem os gráficos e tabelas */
        @page { size: A4 landscape; margin: 15mm; }
        
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: white !important;
            color: #1a202c;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }

        /* REMOVE OS CARACTERES ESTRANHOS (Ícones FontAwesome e Material) */
        i, .fa, .fas, .far, .fal, .fad, .material-icons, 
        [class^="icon-"], [class*=" icon-"], .material-symbols-outlined {
            display: none !important;
        }

        /* Impede que tabelas e gráficos sejam cortados ao meio */
        table { page-break-inside: avoid !important; margin-top: 15px; }
        tr { page-break-inside: avoid; }
        canvas { page-break-inside: avoid !important; max-width: 100% !important; height: auto !important; margin: 10px auto; display: block; }
        .chart-container { page-break-inside: avoid !important; }

        /* Quebras de página forçadas antes das seções principais */
        .page-break {
            page-break-before: always !important;
            display: block;
            height: 1px;
            margin: 0;
        }

        /* Ajuste dos títulos para não ficarem órfãos */
        h1, h2, h3 { page-break-after: avoid !important; }
        
        /* Esconde botões e menus de navegação que não devem ir pro PDF */
        .btn, .actions, .no-print, #barra-edicao { display: none !important; }
    }
</style>
"""

# Adiciona o CSS no final do head
if '</head>' in c:
    c = c.replace('</head>', css + '\n</head>', 1)

# 3. Injeta quebras de página nos títulos principais
# Remove quebras antigas para não duplicar
c = re.sub(r'<div class="page-break"></div>', '', c)

# Procura os títulos e insere a div de quebra antes deles
titulos = [
    'Sumário Executivo',
    'Indicadores Gerais',
    'Ranking dos CORENs',
    'Participação dos Principais',
    'Projeção para Encerramento',
    'Conclusão'
]

for titulo in titulos:
    # Procura <h2> ou <h1> ou <div> que contenham o título
    padrao = rf'(<h[1-3][^>]*>.*?{titulo}.*?</h[1-3]>)'
    c = re.sub(padrao, r'<div class="page-break"></div>\n\1', c, flags=re.IGNORECASE)

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] CSS de paginação injetado e quebras de página adicionadas!")
print("-> Formato Paisagem ativado")
print("-> Caracteres estranhos (ícones) ocultados")
print("-> Quebras de página inseridas antes dos títulos principais")
