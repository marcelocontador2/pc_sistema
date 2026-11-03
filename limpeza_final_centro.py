import re, shutil, datetime, unicodedata

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_centro_custos_v2.html"

shutil.copy2(arquivo, f"{arquivo}.bak_limpeza_final_{ts}")
c = open(arquivo, encoding='utf-8').read()

print("--- LIMPEZA E AJUSTES ---")

# 1. Remove TODOS os caracteres não-ASCII que não sejam acentos portugueses legítimos
#    (Isso elimina emojis, símbolos estranhos e afins que causam a bagunça de caracteres)
def limpar_caracteres(texto):
    resultado = []
    for char in texto:
        # Mantém ASCII padrão (código < 128)
        if ord(char) < 128:
            resultado.append(char)
        # Mantém acentos e cedilha portugueses (Latin-1 Supplement e Extended-A)
        elif '\u00C0' <= char <= '\u017F':
            resultado.append(char)
        # Mantém travessão e aspas tipográficas comuns
        elif char in '\u2013\u2014\u2018\u2019\u201C\u201D\u2026':
            resultado.append(char)
        # Descarta o resto (emojis, símbolos de disquete, etc)
    return ''.join(resultado)

c = limpar_caracteres(c)
print("[OK] Caracteres estranhos (emojis/símbolos) removidos!")

# 2. Adiciona CSS para consertar o grid 2x2 e limpar a impressão
css_impressao = """
    <style>
        @media print {
            /* Força o grid de cards do Sumário a ficar em 2 colunas (2x2) */
            .cards-grid, .grid-kpis, .cards-container {
                display: grid !important;
                grid-template-columns: 1fr 1fr !important;
                gap: 20px !important;
            }

            /* Cada card ocupa uma célula, com altura uniforme */
            .card, .kpi-card {
                box-sizing: border-box !important;
                width: 100% !important;
                min-width: 0 !important;
                padding: 20px !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: center !important;
            }

            /* Títulos e valores não quebram de forma estranha */
            .card-title, .kpi-title {
                font-size: 12px !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
            }
            .card-value, .kpi-value, [id^="kpi-"] {
                font-size: 22px !important;
                white-space: nowrap !important;
            }

            /* Nome do Maior Centro de Custo pode quebrar em até 3 linhas */
            #kpi-maior-centro {
                font-size: 14px !important;
                line-height: 1.3 !important;
                white-space: normal !important;
            }

            /* Esconde botões e elementos que não são do relatório */
            button, .btn, .no-print, .fab, .material-icons { display: none !important; }

            /* Evita que o texto invisível apareça antes das páginas */
            body::before, body::after { display: none !important; content: none !important; }
        }
    </style>
"""

if '</head>' in c:
    c = c.replace('</head>', css_impressao + '\n</head>', 1)
else:
    c += css_impressao

print("[OK] CSS do grid 2x2 e limpeza injetado!")

# 3. Adiciona quebras de página para garantir a paginação correta
# Força quebra antes de cada bloco principal (Sumário, Tabela, Gráfico, Composição, Conclusão)
c = re.sub(r'(<h2[^>]*>\s*Sumário Executivo)', r'<div style="page-break-before: always;"></div>\1', c)
c = re.sub(r'(<h2[^>]*>\s*Tabela Detalhada)', r'<div style="page-break-before: always;"></div>\1', c)
c = re.sub(r'(<h2[^>]*>\s*LEITURA DO GRÁFICO)', r'<div style="page-break-before: always;"></div>\1', c)
c = re.sub(r'(<center[^>]*>\s*COMPOSIÇÃO)', r'<div style="page-break-before: always;"></div>\1', c)
c = re.sub(r'(<h2[^>]*>\s*1\. Conclusão)', r'<div style="page-break-before: always;"></div>\1', c)
print("[OK] Quebras de página injetadas!")

# 4. Salva
open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Relatório limpo, com grid 2x2 e paginação correta!")
