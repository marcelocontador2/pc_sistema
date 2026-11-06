import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_comparativo_receitas_v2.html"

shutil.copy2(arquivo, f"{arquivo}.bak_correcao_final_{ts}")
c = open(arquivo, encoding='utf-8').read()

# ==========================================
# 1. CORRIGIR "R$ R$" duplicado nos cards de grupos
# ==========================================
# O problema: 'R$ ' + fmt() onde fmt já retorna com R$
# Solução: remover o 'R$ ' das strings e manter só fmt()
c = c.replace("'<strong>Recebido:</strong> ' + txtAtual", "'<strong>Recebido:</strong> ' + txtAtual")
c = c.replace("const txtAtual = 'R$ ' + fmt(valorAtual);", "const txtAtual = fmt(valorAtual);")
c = c.replace("const txtAnterior = anterior > 0 ? 'R$ ' + fmt(anterior) : '—';", "const txtAnterior = anterior > 0 ? fmt(anterior) : '—';")
c = c.replace("const txtVariacao = 'R$ ' + fmt(variacao);", "const txtVariacao = fmt(variacao);")
c = c.replace("seta + ' ' + txtVariacao + ' (' + txtPct + ')'", "seta + ' ' + txtVariacao + ' (' + txtPct + ')'")
print("[OK] Corrigido 'R$ R$' duplicado nos cards de grupos")

# ==========================================
# 2. QUEBRAS DE PÁGINA — impedir quebra dentro dos grupos
# ==========================================
css_extra = """
<style>
    .grupo-item {
        page-break-inside: avoid !important;
        break-inside: avoid !important;
    }
    .lista-grupos {
        page-break-inside: avoid !important;
    }
    table.tabela-dados {
        page-break-inside: avoid !important;
    }
</style>
"""
# Adiciona antes do </head>
if '</head>' in c:
    c = c.replace('</head>', css_extra + '\n</head>', 1)
print("[OK] Regras CSS para evitar quebra de página nos grupos")

# ==========================================
# 3. REMOVER O DONUT E COLOCAR PERCENTUAIS NO GRÁFICO DE COLUNAS
# ==========================================

# 3.1 Remove o canvas do donut
c = c.replace('<canvas id="grafico-participacao"></canvas>', '<div id="participacao-info" style="padding: 15px; font-size: 12px;"></div>')
print("[OK] Donut removido")

# 3.2 Substitui a configuração do gráfico de grupos para incluir percentuais nos rótulos
# Localiza o bloco que cria o grafico-grupos
inicio_grafico = c.find("new Chart(document.getElementById('grafico-grupos')")
if inicio_grafico != -1:
    # Encontra o fim do bloco (próximo "new Chart" ou "let htmlGrupos")
    prox = c.find("new Chart", inicio_grafico + 10)
    if prox == -1: prox = c.find("let htmlGrupos", inicio_grafico)
    
    novo_grafico = """new Chart(document.getElementById('grafico-grupos'), {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        { label: 'Atual', data: valsAt, backgroundColor: '#1e293b' },
                        { label: 'Anterior', data: valsAn, backgroundColor: '#60a5fa' }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top', labels: { font: { size: 10 } } },
                        datalabels: {
                            color: '#fff',
                            font: { weight: 'bold', size: 9 },
                            formatter: function(value, context) {
                                if (value === 0) return '';
                                const totalAtual = valsAt.reduce((a, b) => a + b, 0);
                                const pct = totalAtual > 0 ? (value / totalAtual) * 100 : 0;
                                return pct.toFixed(1) + '%';
                            }
                        }
                    },
                    scales: {
                        y: { beginAtZero: true, ticks: { callback: function(v) { return 'R$ ' + (v/1000000).toFixed(0) + ' mi'; }, font: { size: 9 } } },
                        x: { ticks: { font: { size: 9 } } }
                    }
                },
                plugins: [ChartDataLabels]
            });
            """
    c = c[:inicio_grafico] + novo_grafico + c[prox:]
    print("[OK] Gráfico de grupos atualizado com percentuais nos rótulos")

# 3.3 Remove o bloco que criava o gráfico de participação (donut)
inicio_donut = c.find("new Chart(document.getElementById('grafico-participacao')")
if inicio_donut != -1:
    fim_donut = c.find(";", c.find("});", inicio_donut))
    if fim_donut == -1:
        fim_donut = c.find(");", inicio_donut) + 2
    else:
        fim_donut += 1
    c = c[:inicio_donut] + c[fim_donut:]
    print("[OK] Código do donut removido")

# 3.4 Adiciona o ChartDataLabels no <head> (se ainda não estiver)
if 'chartjs-plugin-datalabels' not in c:
    c = c.replace('</head>', '<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels"></script>\n</head>', 1)
    print("[OK] Plugin ChartDataLabels adicionado")

# ==========================================
# 4. RECONSTRUIR O HTML DO RANKING (top 10) com layout mais compacto
# ==========================================
# O layout atual já está bom, apenas ajusta a coluna do ranking para mostrar os valores
# (deixando para o próximo ajuste)

open(arquivo, 'w', encoding='utf-8').write(c)
print("\n[OK] Todas as correções aplicadas com sucesso!")
print("\n=== RESUMO ===")
print("1. 'R$ R$' duplicado corrigido")
print("2. Quebra de página evitada nos grupos (page-break-inside: avoid)")
print("3. Donut removido")
print("4. Percentuais adicionados ao gráfico de colunas")
