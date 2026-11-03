import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_centro_custos_v2.html"

# Cria backup do estado atual (antes de limpar)
shutil.copy2(arquivo, f"{arquivo}.bak_limpeza_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Remove qualquer <style> que tenha sido injetado por nós nas tentativas anteriores
# (Vamos remover os blocos que contêm as palavras-chave que usamos)
c = re.sub(r'<style>.*?@media print.*?</style>', '', c, flags=re.DOTALL)
c = re.sub(r'<style>.*?\.sumario-grid.*?</style>', '', c, flags=re.DOTALL)

# 2. Injeta o novo CSS limpo e à prova de falhas no final do <head>
css_limpo = """
    <style>
        @media print {
            /* Força os cards a ficarem em linha e não estourar a tela */
            .cards-container, .grid-kpis, .cards-grid, div[style*="display: grid"] {
                display: flex !important;
                flex-wrap: nowrap !important;
                justify-content: space-between !important;
                gap: 10px !important;
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
                padding: 0 10px !important;
            }

            /* Garante que cada card ocupe exatamente o mesmo espaço */
            .card, .kpi-card, .resumo-card {
                flex: 1 1 0px !important;
                min-width: 0 !important;
                padding: 15px !important;
                box-sizing: border-box !important;
                overflow: hidden !important;
            }

            /* Impede o R$ de quebrar de linha */
            #kpi-total-atual, #kpi-media-atual, #kpi-variacao, 
            #kpi-total-anterior, #kpi-maior-valor {
                white-space: nowrap !important;
                font-size: 16px !important; /* Fonte um pouco menor para caber */
                display: block !important;
            }

            /* Trata o nome gigante do centro de custo */
            #kpi-maior-centro {
                font-size: 11px !important;
                line-height: 1.2 !important;
                white-space: normal !important;
                word-wrap: break-word !important;
                display: -webkit-box !important;
                -webkit-line-clamp: 3 !important; /* Limita a 3 linhas */
                -webkit-box-orient: vertical !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
            }

            /* Títulos dos cards */
            .card-title, .kpi-title {
                font-size: 10px !important;
                margin-bottom: 5px !important;
                white-space: normal !important;
            }
        }
    </style>
"""

if '</head>' in c:
    c = c.replace('</head>', css_limpo + '\n</head>', 1)
else:
    c += css_limpo

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Código limpo, CSS injetado com segurança e sem quebrar o JavaScript!")
