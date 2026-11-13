import re

c = open('relatorio_final.html', encoding='utf-8-sig').read()

# 1. Ajusta o CSS global (tamanhos de fontes, padding, alturas)
css_ajustes = """
        /* Ajustes de layout para caber em páginas A4 */
        .page {
            padding: 30px 50px;
            height: 100vh;
            max-height: 100vh;
            overflow: hidden;
        }
        .section-title {
            font-size: 26px;
            margin: 0 0 20px 0;
        }
        .cards-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }
        .card { padding: 18px; }
        .card .card-value { font-size: 22px; }
        
        /* Tabelas mais compactas */
        th { padding: 8px 10px; font-size: 11px; }
        td { padding: 8px 10px; font-size: 12px; }
        .table-container { max-height: 100%; overflow: hidden; }
        
        /* Gráficos com altura controlada */
        .chart-box canvas { max-height: 280px !important; }
        .chart-container { gap: 20px; margin-bottom: 15px; }
        
        /* Leitura do gráfico mais compacta */
        .leitura-box { padding: 15px; }
        .leitura-box h3 { font-size: 12px; margin-bottom: 8px; }
        .leitura-box ul { font-size: 12px; line-height: 1.5; }
        
        /* Tabela mensal compacta */
        #tabela-mensal td, #tabela-mensal th { padding: 5px 8px; font-size: 11px; }
        
        /* Composição: donut menor */
        .donut-container { max-width: 380px; margin: 0 auto; }
"""

# Adiciona os ajustes no final do <style> (antes de </style>)
if '/* Ajustes de layout para caber em páginas A4 */' not in c:
    c = c.replace('</style>', css_ajustes + '\n    </style>')
    print("[OK] CSS ajustado para caber em páginas A4!")

# 2. Ajusta a página de Tendência (gráfico + leitura + tabela)
trend_old = re.search(r'<!-- GRÁFICO DE TENDÊNCIA -->.*?</div>\s*</div>\s*</div>', c, re.DOTALL)
if trend_old:
    trend_new = '''<!-- GRÁFICO DE TENDÊNCIA -->
    <div class="page">
        <div class="section-subtitle">TENDÊNCIA</div>
        <h2 class="section-title">Evolução Mensal do Total Geral</h2>
        <div class="chart-container" style="margin-bottom: 20px;">
            <div class="chart-box" style="flex: 1.5; max-height: 300px;">
                <canvas id="grafico-tendencia" style="max-height: 280px;"></canvas>
            </div>
            <div class="leitura-box" style="flex: 1; max-height: 300px; overflow-y: auto;">
                <h3>LEITURA DO GRÁFICO</h3>
                <ul id="leitura-tendencia">
                    <li>Carregando...</li>
                </ul>
            </div>
        </div>
        
        <div class="table-container" style="margin-top: 15px; max-height: 320px; overflow-y: auto;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr>
                        <th>Mês</th>
                        <th class="text-right">Total Atual (R$)</th>
                        <th class="text-right">Total Anterior (R$)</th>
                        <th class="text-right">Variação (R$)</th>
                        <th class="text-right">Variação (%)</th>
                    </tr>
                </thead>
                <tbody id="tabela-mensal"></tbody>
            </table>
        </div>
    </div>'''
    c = re.sub(r'<!-- GRÁFICO DE TENDÊNCIA -->.*?</div>\s*</div>\s*</div>', trend_new, c, flags=re.DOTALL)
    print("[OK] Página de tendência ajustada!")

# 3. Ajusta a página de Composição (donut + tabela)
comp_old = re.search(r'<!-- GRÁFICO DE COMPOSIÇÃO -->.*?</div>\s*</div>\s*</div>', c, re.DOTALL)
if comp_old:
    comp_new = '''<!-- GRÁFICO DE COMPOSIÇÃO -->
    <div class="page">
        <div class="section-subtitle">COMPOSIÇÃO</div>
        <h2 class="section-title">Distribuição do Gasto</h2>
        <div class="chart-container">
            <div class="chart-box donut-container" style="flex: 1; max-width: 380px;">
                <canvas id="grafico-donut" style="max-height: 320px;"></canvas>
            </div>
            <div style="flex: 1.2; max-height: 380px; overflow-y: auto;">
                <div class="table-container">
                    <table id="tabela-composicao">
                        <thead>
                            <tr>
                                <th>Centro de Custo</th>
                                <th class="text-right">Total (R$)</th>
                                <th class="text-right">%</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>'''
    c = re.sub(r'<!-- GRÁFICO DE COMPOSIÇÃO -->.*?</div>\s*</div>\s*</div>', comp_new, c, flags=re.DOTALL)
    print("[OK] Página de composição ajustada!")

open('relatorio_final.html', 'w', encoding='utf-8').write(c)
print("[OK] relatorio_final.html atualizado com layout de páginas ajustado!")
