import re

c = open('relatorio_final.html', encoding='utf-8-sig').read()

# Encontra a seção de composição
padrao = r'<!-- GRÁFICO DE COMPOSIÇÃO -->.*?</div>\s*</div>\s*</div>'

novo_bloco = '''<!-- GRÁFICO DE COMPOSIÇÃO -->
    <div class="page">
        <div class="section-subtitle">COMPOSIÇÃO</div>
        <h2 class="section-title">Distribuição do Gasto por Centro de Custo</h2>
        
        <div style="display: flex; gap: 40px; align-items: flex-start; justify-content: space-between;">
            <!-- Donut à esquerda -->
            <div style="flex: 1; max-width: 450px;">
                <canvas id="grafico-donut" style="max-height: 380px;"></canvas>
            </div>
            
            <!-- Tabela à direita -->
            <div style="flex: 1.5;">
                <div class="table-container" style="box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
                    <table id="tabela-composicao" style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr>
                                <th style="padding: 16px 20px; font-size: 13px;">Centro de Custo</th>
                                <th style="padding: 16px 20px; font-size: 13px;" class="text-right">Total (R$)</th>
                                <th style="padding: 16px 20px; font-size: 13px;" class="text-right">%</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>'''

if re.search(padrao, c, re.DOTALL):
    c = re.sub(padrao, novo_bloco, c, flags=re.DOTALL)
    print("[OK] Layout da composição ajustado (donut à esquerda, tabela à direita)!")
else:
    print("[AVISO] Bloco da composição não encontrado. Tentando abordagem alternativa...")
    if 'id="grafico-donut"' in c:
        inicio = c.find('<!-- GRÁFICO DE COMPOSIÇÃO -->')
        fim = c.find('<!-- CONCLUSÃO -->', inicio)
        if fim == -1:
            fim = c.find('<!--', inicio + 10)
        if fim != -1:
            c = c[:inicio] + novo_bloco + c[fim:]
            print("[OK] Layout ajustado manualmente!")

# Ajusta o CSS da tabela de composição para ficar mais bonita
css_table = """
        /* Estilo refinado para a tabela de composição */
        #tabela-composicao th {
            background: var(--primary);
            color: #fff;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        #tabela-composicao td {
            padding: 14px 20px;
            font-size: 13px;
            border-bottom: 1px solid var(--border-color);
        }
        #tabela-composicao tr:nth-child(even) {
            background: #f8fafc;
        }
        #tabela-composicao tr:hover {
            background: #edf2f7;
        }
"""
if '#tabela-composicao th' not in c:
    c = c.replace('</style>', css_table + '</style>')

open('relatorio_final.html', 'w', encoding='utf-8').write(c)
print("[OK] relatorio_final.html atualizado!")
