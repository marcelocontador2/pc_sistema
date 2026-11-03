import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. CORRIGIR O BACKEND (main.py)
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_fix_rota_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

# Troca a URL do Playwright da v2 para a original
c_back = c_back.replace(
    'http://127.0.0.1:9994/relatorio_centro_custos_v2?historico_id={historico_id}',
    'http://127.0.0.1:9994/relatorio_centro_custos?historico_id={historico_id}'
)
open(back_path, 'w', encoding='utf-8').write(c_back)
print("[OK] Backend corrigido para abrir o relatório ORIGINAL (sem v2)!")

# ==========================================
# 2. AJUSTAR O ARQUIVO ORIGINAL (relatorio_centro_custos.html)
# ==========================================
arquivo_original = r"pc_frontend\relatorio_centro_custos.html"
shutil.copy2(arquivo_original, f"{arquivo_original}.bak_fix_original_{ts}")
c = open(arquivo_original, encoding='utf-8').read()

# A. Limpa caracteres estranhos (emojis e ícones invisíveis)
c = re.sub(r'[\x80-\xff]{5,}', '', c)

# B. Injeta o Espião (para ler os dados do histórico)
espiao = """
    <script id="interceptar_historico">
        (function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');
            
            if (historicoId) {
                const originalFetch = window.fetch;
                window.fetch = function(url, options) {
                    if (url.includes('/api/relatorio_v2/') || url.includes('/api/centro_custos/')) {
                        return originalFetch(`/historico_centro_custos/${historicoId}`, options)
                            .then(res => res.json())
                            .then(data => {
                                const dados = data.dados ? data.dados : data;
                                const centros = dados.centros || [];
                                const centrosAnt = dados.centros_anterior || [];

                                const totalAtual = centros.reduce((acc, c) => acc + c.valor, 0);
                                const totalAnterior = centrosAnt.reduce((acc, c) => acc + c.valor, 0);
                                const variacao_pct = totalAnterior > 0 ? ((totalAtual - totalAnterior) / totalAnterior) * 100 : 0;
                                
                                let maiorCentro = { nome: "Nenhum", valor: 0 };
                                if (centros.length > 0) {
                                    maiorCentro = centros.reduce((max, c) => c.valor > max.valor ? c : max, centros[0]);
                                }

                                const respostaFinal = {
                                    atual: { total: totalAtual, media_mensal: totalAtual / 9, maior_centro: maiorCentro },
                                    anterior: { total: totalAnterior, media_mensal: totalAnterior / 9 },
                                    variacao_pct: variacao_pct,
                                    centros: centros,
                                    centros_anterior: centrosAnt
                                };

                                return new Response(JSON.stringify(respostaFinal), { 
                                    headers: { 'Content-Type': 'application/json' } 
                                });
                            });
                    }
                    return originalFetch(url, options);
                };
            }
        })();
    </script>
"""
if '</body>' in c:
    c = c.replace('</body>', espiao + '\n</body>', 1)
else:
    c += espiao

# C. Injeta CSS de impressão para deixar o PDF impecável
css_impressao = """
    <style>
        @media print {
            /* Esconde botões e ícones que causam os caracteres estranhos */
            button, .btn, .no-print, i, .fa, .fas, .far, .material-icons { display: none !important; }

            /* Força o grid 2x2 nos cards do sumário */
            .cards-grid, .grid-kpis, .cards-container {
                display: grid !important;
                grid-template-columns: 1fr 1fr !important;
                gap: 20px !important;
                page-break-inside: avoid !important;
            }

            /* Ajusta os cards para não vazar */
            .card, .kpi-card {
                width: 100% !important;
                box-sizing: border-box !important;
                padding: 15px !important;
                page-break-inside: avoid !important;
            }

            /* Valores financeiros não podem quebrar linha */
            .card-value, .kpi-value {
                font-size: 18px !important;
                white-space: nowrap !important;
            }
            
            /* Garante que o gráfico seja impresso */
            canvas { max-width: 100% !important; height: auto !important; }
        }
    </style>
"""
if '</head>' in c:
    c = c.replace('</head>', css_impressao + '\n</head>', 1)

open(arquivo_original, 'w', encoding='utf-8').write(c)
print("[OK] Arquivo original limpo e com as regras de impressão injetadas!")

# Validação da sintaxe do Python
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py 100% validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro no main.py: {e}")
