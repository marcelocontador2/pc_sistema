import re

c = open('relatorio_final.html', encoding='utf-8-sig').read()

# 1. Encontra o final da página de tendência (após o fechamento da tabela mensal)
# Vamos procurar o fechamento da div "page" que contém a tabela mensal
padrao = r'(<!-- GRÁFICO DE TENDÊNCIA -->.*?</div>\s*</div>\s*</div>)'

# A seção de composição completa
secao_composicao = '''
    <!-- GRÁFICO DE COMPOSIÇÃO -->
    <div class="page">
        <div class="section-subtitle">COMPOSIÇÃO</div>
        <h2 class="section-title">Distribuição do Gasto por Centro de Custo</h2>
        <div class="chart-container">
            <div class="chart-box donut-container" style="flex: 1; max-width: 400px;">
                <canvas id="grafico-donut" style="max-height: 350px;"></canvas>
            </div>
            <div style="flex: 1.2; max-height: 400px; overflow-y: auto;">
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
    </div>
'''

# Verifica se a seção já existe
if 'id="grafico-donut"' not in c:
    # Encontra a página de tendência e insere a seção de composição após ela
    match = re.search(padrao, c, re.DOTALL)
    if match:
        # Pega o final da página de tendência
        fim_tendencia = match.end()
        c = c[:fim_tendencia] + secao_composicao + c[fim_tendencia:]
        print("[OK] Seção de composição (donut + tabela) restaurada!")
    else:
        print("[ERRO] Página de tendência não encontrada. Tentando inserir antes da conclusão...")
        # Fallback: insere antes da seção de conclusão
        pos_conclusao = c.find('<!-- CONCLUSÃO -->')
        if pos_conclusao != -1:
            c = c[:pos_conclusao] + secao_composicao + c[pos_conclusao:]
            print("[OK] Seção de composição inserida antes da conclusão!")
        else:
            print("[ERRO] Não foi possível encontrar o local para inserir.")
else:
    print("[AVISO] A seção de composição já existe no arquivo.")

open('relatorio_final.html', 'w', encoding='utf-8').write(c)
print("[OK] relatorio_final.html atualizado!")
