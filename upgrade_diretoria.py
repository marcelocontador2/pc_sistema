import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. CRIAR O RELATÓRIO EXECUTIVO (NÍVEL DIRETORIA)
# ==========================================
html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        @page { size: A4 landscape; margin: 0; }
        
        * { box-sizing: border-box; }
        
        body {
            font-family: 'Inter', sans-serif;
            background: #ffffff;
            margin: 0;
            padding: 0;
            color: #1e293b;
            -webkit-print-color-adjust: exact;
        }

        .page {
            width: 297mm;
            height: 210mm;
            padding: 20mm;
            display: flex;
            flex-direction: column;
        }

        /* CABEÇALHO CORPORATIVO */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #0f172a;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }

        .header-left h1 {
            margin: 0;
            font-size: 32px;
            font-weight: 700;
            color: #0f172a;
            letter-spacing: -0.5px;
        }

        .header-left p {
            margin: 5px 0 0 0;
            font-size: 16px;
            color: #64748b;
            font-weight: 400;
        }

        .header-right {
            text-align: right;
        }

        .header-right .periodo {
            font-size: 18px;
            font-weight: 700;
            color: #0f172a;
        }

        .header-right .data {
            font-size: 12px;
            color: #64748b;
            margin-top: 5px;
        }

        /* CARDS DE KPI */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }

        .kpi-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 20px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }

        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 5px; height: 100%;
            background: #0f172a;
        }

        .kpi-card.verde::before { background: #10b981; }
        .kpi-card.vermelho::before { background: #ef4444; }
        .kpi-card.dourado::before { background: #f59e0b; }

        .kpi-title {
            font-size: 13px;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .kpi-value {
            font-size: 28px;
            font-weight: 700;
            color: #0f172a;
        }

        .kpi-card.verde .kpi-value { color: #10b981; }
        .kpi-card.vermelho .kpi-value { color: #ef4444; }

        /* ÁREA DO GRÁFICO */
        .chart-area {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 20px;
            height: 250px;
            display: flex;
            justify-content: center;
            align-items: center;
            flex: 1;
        }

        /* RODAPÉ */
        .footer {
            margin-top: 20px;
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: #94a3b8;
            border-top: 1px solid #e2e8f0;
            padding-top: 10px;
        }
    </style>
</head>
<body>
    <div class="page">
        <!-- CABEÇALHO -->
        <div class="header">
            <div class="header-left">
                <h1>Relatório Executivo</h1>
                <p>Panorama de Resultados Contábeis e Orçamentários</p>
            </div>
            <div class="header-right">
                <div class="periodo" id="periodo-titulo">Carregando...</div>
                <div class="data">Emissão: <span id="data-emissao"></span></div>
            </div>
        </div>

        <!-- BLOCO 1: INDICADORES PATRIMONIAIS E ORÇAMENTÁRIOS -->
        <div class="kpi-grid" id="kpis-topo">
            <!-- Injetados via JS -->
        </div>

        <!-- BLOCO 2: GRÁFICO E RESULTADOS -->
        <div style="display: flex; gap: 20px; flex: 1;">
            <!-- Resultados Consolidados -->
            <div style="flex: 1; display: flex; flex-direction: column; gap: 15px;">
                <div class="kpi-card dourado">
                    <div class="kpi-title">Resultado Orçamentário</div>
                    <div class="kpi-value" id="res-orcamentario">R$ 0</div>
                </div>
                <div class="kpi-card dourado">
                    <div class="kpi-title">Resultado Patrimonial</div>
                    <div class="kpi-value" id="res-patrimonial">R$ 0</div>
                </div>
                <div class="kpi-card dourado">
                    <div class="kpi-title">Resultado Financeiro</div>
                    <div class="kpi-value" id="res-financeiro">R$ 0</div>
                </div>
            </div>
            
            <!-- Gráfico de Receitas vs Despesas -->
            <div class="chart-area" style="flex: 2;">
                <canvas id="graficoResultados"></canvas>
            </div>
        </div>

        <!-- RODAPÉ -->
        <div class="footer">
            <div>SGPC - Sistema de Gestão de Prestação de Contas</div>
            <div>Documento Confidencial - Uso Exclusivo da Diretoria</div>
        </div>
    </div>

    <script>
        function moeda(v) {
            if (!v) return "R$ 0";
            return Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 0, maximumFractionDigits: 0 });
        }

        function resumido(v) {
            if (!v) return "R$ 0 mi";
            const num = Number(v) / 1000000;
            return (num < 0 ? "-R$ " : "R$ ") + Math.abs(num).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " mi";
        }

        document.addEventListener('DOMContentLoaded', async function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');
            document.getElementById("data-emissao").innerText = new Date().toLocaleDateString('pt-BR') + " às " + new Date().toLocaleTimeString('pt-BR');

            if (!historicoId) return;

            try {
                const res = await fetch(`/historico_panorama/${historicoId}`);
                const data = await res.json();
                const d = data.dados;

                document.getElementById("periodo-titulo").innerText = data.periodo || "Período";

                // 1. Preenche KPIs superiores
                document.getElementById("kpis-topo").innerHTML = `
                    <div class="kpi-card">
                        <div class="kpi-title">Ativo Total (BP)</div>
                        <div class="kpi-value">${resumido(d.ativo_total)}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">Passivo Total (BP)</div>
                        <div class="kpi-value">${resumido(d.passivo_total)}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">Patrimônio Líquido</div>
                        <div class="kpi-value">${resumido(d.patrimonio_liquido)}</div>
                    </div>
                `;

                // 2. Preenche resultados inferiores com cores dinâmicas
                const orc = d.superavit_orcamentario || 0;
                const pat = d.superavit_patrimonial || 0;
                const fin = d.superavit_financeiro || 0;

                const elOrc = document.getElementById("res-orcamentario");
                elOrc.innerText = resumido(orc);
                elOrc.style.color = orc < 0 ? "#ef4444" : "#10b981";

                const elPat = document.getElementById("res-patrimonial");
                elPat.innerText = resumido(pat);
                elPat.style.color = pat < 0 ? "#ef4444" : "#10b981";

                const elFin = document.getElementById("res-financeiro");
                elFin.innerText = resumido(fin);
                elFin.style.color = fin < 0 ? "#ef4444" : "#10b981";

                // 3. Monta o Gráfico Comparativo
                const ctx = document.getElementById('graficoResultados').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: ['Receitas Realizadas', 'Despesas Empenhadas'],
                        datasets: [{
                            label: 'Valor (R$)',
                            data: [d.receita_realizada, d.despesa_empenhada],
                            backgroundColor: ['#10b981', '#ef4444'],
                            borderRadius: 6,
                            barPercentage: 0.5
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            title: {
                                display: true,
                                text: 'Comparativo de Receitas x Despesas (Realizadas)',
                                font: { size: 14, family: 'Inter', weight: 'bold' },
                                color: '#0f172a',
                                padding: { bottom: 20 }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: { color: '#f1f5f9' },
                                ticks: {
                                    callback: function(value) {
                                        return 'R$ ' + (value / 1000000).toFixed(0) + ' mi';
                                    },
                                    font: { family: 'Inter' }
                                }
                            },
                            x: {
                                grid: { display: false },
                                ticks: { font: { family: 'Inter', weight: 'bold' } }
                            }
                        }
                    }
                });

            } catch (e) {
                console.error("Erro", e);
            }
        });
    </script>
</body>
</html>"""

with open(r"pc_frontend\relatorio_panorama.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("[OK] Layout Nível Diretoria (com gráficos) criado!")

# ==========================================
# 2. FORÇAR A ROTA NO MAIN.PY
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_diretoria_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

# Caça e substitui a rota do Playwright à força
c_back = re.sub(
    r'url = f"http://127\.0\.0\.1:9994/panorama\?historico_id=\{historico_id\}&_t=\{int\(time\.time\(\)\)\}"',
    'url = f"http://127.0.0.1:9994/relatorio_panorama?historico_id={historico_id}&_t={int(time.time())}"',
    c_back
)

# Se por algum motivo a regex acima falhar, faz um replace bruto
c_back = c_back.replace(
    'http://127.0.0.1:9994/panorama?historico_id={historico_id}',
    'http://127.0.0.1:9994/relatorio_panorama?historico_id={historico_id}'
)

open(back_path, 'w', encoding='utf-8').write(c_back)
print("[OK] Rota do Playwright forçada para o novo relatório!")

try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe no main.py: {e}")
