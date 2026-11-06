import re, shutil, datetime, os

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_comparativo_receitas_v2.html"
if not os.path.exists(arquivo):
    arquivo = r"pc_frontend\relatorio_comparativo_receitas.html"

shutil.copy2(arquivo, f"{arquivo}.bak_paginacao_3_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Remove QUALQUER div de quebra de página antiga
c = re.sub(r'<div class="page-break"[^>]*>.*?</div>', '', c, flags=re.DOTALL)
c = re.sub(r'<div style="page-break[^>]*>.*?</div>', '', c, flags=re.DOTALL)

# 2. Remove CSS de impressão antigo
c = re.sub(r'<style>\s*@media print.*?</style>', '', c, flags=re.DOTALL)

# 3. Novo CSS: Retrato, Compacto, Força Fonte para Limpar caracteres
css = """
<style>
    @media print {
        /* A4 Retrato */
        @page { size: A4 portrait; margin: 10mm; }
        
        body {
            background: white !important;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
            /* Força uma fonte padrão que não quebra */
            font-family: 'Segoe UI', Arial, Helvetica, sans-serif !important;
        }

        /* OCULTA OS CARACTERES ESTRANHOS (Ícones de fonte que não renderizam) */
        i, .fa, .fas, .far, .fal, .fad, .material-icons, [class^="icon-"], [class*=" icon-"] {
            display: none !important;
            visibility: hidden !important;
            font-size: 0 !important;
        }

        /* Esconde menus de navegação, botões, etc */
        .btn, .actions, .no-print, #barra-edicao, nav, header { display: none !important; }

        /* COMPACTAÇÃO: Reduz margens e tamanhos para caber em menos páginas */
        h1, h2 { font-size: 16px !important; margin-top: 10px !important; margin-bottom: 5px !important; }
        h3 { font-size: 13px !important; margin-top: 10px !important; margin-bottom: 5px !important; }
        p { margin-bottom: 5px !important; font-size: 12px !important; }
        
        /* Compacta as tabelas e cards */
        table { width: 100% !important; border-collapse: collapse !important; margin-bottom: 10px !important; font-size: 11px !important; }
        th, td { padding: 4px 8px !important; }
        .card { padding: 10px !important; margin-bottom: 10px !important; }
        
        /* Garante que tabelas, gráficos e cards não sejam cortados ao meio */
        table, tr, td, th, canvas, .card, .chart-container, .row { 
            page-break-inside: avoid !important; 
        }
        
        /* Evita que os títulos fiquem no final da página sem o conteúdo */
        h1, h2, h3 { page-break-after: avoid !important; }
        
        /* Ajusta o tamanho dos gráficos para não estourarem a página em Retrato */
        canvas { 
            max-width: 100% !important; 
            height: auto !important; 
            max-height: 200px !important; 
            display: block;
            margin: 10px auto;
        }
        
        /* FORÇA QUEBRA APENAS ANTES DA CAPA E DO RANKING (Para dar uma respirada) */
        /* Identifica a segunda página principal pelo título do Ranking */
        h2:contains('Ranking'), h3:contains('Ranking') {
            page-break-before: always !important;
        }
        
        /* Força quebra antes da Projeção também, se necessário */
        h2:contains('Projeção'), h3:contains('Projeção') {
            page-break-before: always !important;
        }
    }
</style>
"""
if '</head>' in c:
    c = c.replace('</head>', css + '\n</head>', 1)

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] CSS de impressao refeito!")
print("-> Modo Retrato ativado.")
print("-> Compactacao aplicada para caber em 3 paginas.")
print("-> Icones ocultados (fim dos caracteres estranhos).")
