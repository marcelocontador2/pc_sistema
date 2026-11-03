import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\panorama.html"

shutil.copy2(arquivo, f"{arquivo}.bak_print_{ts}")
c = open(arquivo, encoding='utf-8').read()

# Verifica se já foi injetado para não duplicar
if "@media print" not in c:
    css_print = """
    <style>
        @media print {
            /* Esconde os botões de ação, filtros e a barra lateral de histórico */
            .actions, 
            .filters, 
            .historico-box,
            .btn-voltar,
            .btn-exibir,
            .btn-excluir,
            .btn-pdf,
            .btn-salvar,
            #lista-historico,
            button {
                display: none !important;
            }

            /* Ajusta o layout principal para ocupar a folha inteira A4 */
            body {
                background: white !important;
                margin: 0 !important;
                padding: 0 !important;
            }

            .container, .main-content, .layout {
                display: block !important;
                width: 100% !important;
                max-width: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
                box-shadow: none !important;
                border: none !important;
            }

            /* Garante que os cards fiquem alinhados em grade */
            .cards-grid, .dashboard-cards, .row {
                display: grid !important;
                grid-template-columns: repeat(3, 1fr) !important;
                gap: 20px !important;
                margin-top: 20px !important;
            }

            /* Dá um visual limpo para os cards no papel */
            .card {
                background: #f8fafc !important;
                border: 1px solid #e2e8f0 !important;
                border-radius: 8px !important;
                padding: 20px !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }

            /* Adiciona um título elegante no topo do PDF */
            .container::before {
                content: "Relatório de Panorama - Resultados Gerais";
                display: block;
                font-size: 24px;
                font-weight: bold;
                color: #1a202c;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #3182ce;
            }
        }
    </style>
    """
    
    # Injeta o CSS antes do fechamento da tag </head>
    if '</head>' in c:
        c = c.replace('</head>', css_print + '\n</head>', 1)
        open(arquivo, 'w', encoding='utf-8').write(c)
        print("[OK] Regra de impressão (@media print) adicionada ao Panorama com sucesso!")
    else:
        print("[ERRO] Tag </head> não encontrada.")
else:
    print("[AVISO] O CSS de impressão já estava no arquivo.")
