import re, shutil, datetime, os

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_comparativo_receitas_v2.html"
if not os.path.exists(arquivo):
    arquivo = r"pc_frontend\relatorio_comparativo_receitas.html"

shutil.copy2(arquivo, f"{arquivo}.bak_pag_final_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Remove TODAS as quebras de página antigas
c = re.sub(r'<div class="page-break"[^>]*>\s*</div>', '', c, flags=re.DOTALL)
c = re.sub(r'<div[^>]*style="[^"]*page-break-before[^"]*"[^>]*>\s*</div>', '', c, flags=re.DOTALL)
c = re.sub(r'<div[^>]*style="[^"]*page-break[^"]*"[^>]*>\s*</div>', '', c, flags=re.DOTALL)

# 2. Remove CSS de impressão antigo
c = re.sub(r'<style>\s*@media print.*?</style>', '', c, flags=re.DOTALL)

# 3. Novo CSS de paginação compacta
css = """
<style>
    @media print {
        /* A4 Retrato com margens pequenas */
        @page { size: A4 portrait; margin: 10mm; }
        
        body {
            background: white !important;
            font-family: 'Segoe UI', Arial, Helvetica, sans-serif !important;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }

        /* Oculta ícones que geram os caracteres estranhos */
        i, .fa, .fas, .far, .fal, .fad, .material-icons, 
        [class^="icon-"], [class*=" icon-"] {
            display: none !important;
            font-size: 0 !important;
        }

        /* Oculta menus, botões, barras de edição */
        .btn, .actions, .no-print, #barra-edicao, nav, header { display: none !important; }

        /* Compacta títulos */
        h1 { font-size: 18px !important; margin: 0 0 8px 0 !important; }
        h2 { font-size: 15px !important; margin: 8px 0 6px 0 !important; }
        h3 { font-size: 13px !important; margin: 8px 0 4px 0 !important; }
        p  { font-size: 11px !important; margin: 3px 0 !important; }

        /* Compacta cards e tabelas */
        .card, .kpi-card { padding: 8px !important; margin: 6px 0 !important; }
        table { width: 100% !important; font-size: 10px !important; margin-bottom: 8px !important; }
        th, td { padding: 3px 5px !important; }

        /* Reduz gráficos para caber 2 seções na mesma página */
        canvas { 
            max-width: 100% !important; 
            max-height: 180px !important;
            height: auto !important; 
            display: block;
            margin: 6px auto;
        }

        /* Impede corte de elementos ao meio */
        table, tr, td, th, canvas, .card, .chart-container {
            page-break-inside: avoid !important;
        }

        /* Evita títulos órfãos no final da página */
        h1, h2, h3 { page-break-after: avoid !important; }

        /* Marca as quebras que inserimos no HTML */
        .page-break { 
            page-break-before: always !important; 
            height: 0; 
            display: block; 
        }

        /* Capa: ocupa a página inteira */
        .capa-print, .cover, .pagina-capa {
            page-break-after: always !important;
            height: auto;
        }
    }
</style>
"""
if '</head>' in c:
    c = c.replace('</head>', css + '\n</head>', 1)

# 4. Insere quebras de página nos pontos estratégicos
# Procuramos os "inícios de seção" pelos títulos

# Marca: SUMÁRIO EXECUTIVO (deve iniciar página 2)
padrao_sumario = r'([^\n]*<h[1-3][^>]*>\s*Sumário Executivo)'
if re.search(padrao_sumario, c, re.IGNORECASE):
    c = re.sub(padrao_sumario, r'<div class="page-break"></div>\n\1', c, count=1, flags=re.IGNORECASE)
    print("[OK] Quebra antes de 'Sumário Executivo' (início pág 2)")

# Marca: COMPOSIÇÃO / Análise por Grupo de Receita (deve iniciar página 3)
padrao_composicao = r'([^\n]*<h[1-3][^>]*>\s*(?:COMPOSIÇÃO|Composição|Análise por Grupo))'
if re.search(padrao_composicao, c, re.IGNORECASE):
    c = re.sub(padrao_composicao, r'<div class="page-break"></div>\n\1', c, count=1, flags=re.IGNORECASE)
    print("[OK] Quebra antes de 'Composição' (início pág 3)")

# Marca: RANKING (deve iniciar página 4)
padrao_ranking = r'([^\n]*<h[1-3][^>]*>\s*Ranking dos CORENs)'
if re.search(padrao_ranking, c, re.IGNORECASE):
    c = re.sub(padrao_ranking, r'<div class="page-break"></div>\n\1', c, count=1, flags=re.IGNORECASE)
    print("[OK] Quebra antes de 'Ranking dos CORENs' (início pág 4)")

# Marca: PROJEÇÃO (deve iniciar página 5)
padrao_projecao = r'([^\n]*<h[1-3][^>]*>\s*Projeção para Encerramento)'
if re.search(padrao_projecao, c, re.IGNORECASE):
    c = re.sub(padrao_projecao, r'<div class="page-break"></div>\n\1', c, count=1, flags=re.IGNORECASE)
    print("[OK] Quebra antes de 'Projeção' (início pág 5)")

open(arquivo, 'w', encoding='utf-8').write(c)

print()
print("=== ESTRUTURA DE PÁGINAS ===")
print("Pag 1: Capa")
print("Pag 2: Sumario Executivo + Indicadores")
print("Pag 3: Composicao por Grupo (grafico de barras)")
print("Pag 4: Ranking + Participacao (donut)")
print("Pag 5: Projecao + Conclusao")
print()
print("-> Modo Retrato ativado")
print("-> Icones ocultados (fim dos caracteres estranhos)")
print("-> Graficos reduzidos para caber 2 secoes por pagina")
