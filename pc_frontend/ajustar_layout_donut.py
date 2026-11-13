import re

c = open('relatorio_final.html', encoding='utf-8-sig').read()

# Encontra a seção de composição (do comentário até o fechamento da div .page)
padrao = r'<!-- GRÁFICO DE COMPOSIÇÃO -->.*?</div>\s*</div>\s*</div>'

novo_bloco = '''<!-- GRÁFICO DE COMPOSIÇÃO -->
    <div class="page">
        <div class="section-subtitle">COMPOSIÇÃO</div>
        <h2 class="section-title">Distribuição do Gasto por Centro de Custo</h2>
        
        <!-- Donut em cima -->
        <div class="donut-container" style="max-width: 450px; margin: 0 auto 20px auto;">
            <canvas id="grafico-donut" style="max-height: 320px;"></canvas>
        </div>
        
        <!-- Tabela embaixo, ocupando largura total -->
        <div class="table-container" style="max-height: 380px; overflow-y: auto;">
            <table id="tabela-composicao" style="width: 100%;">
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
    </div>'''

if re.search(padrao, c, re.DOTALL):
    c = re.sub(padrao, novo_bloco, c, flags=re.DOTALL)
    print("[OK] Layout da composição ajustado (donut em cima, tabela embaixo)!")
else:
    print("[AVISO] Bloco da composição não encontrado. Tentando abordagem alternativa...")
    # Tenta encontrar pelo id do canvas
    if 'id="grafico-donut"' in c:
        # Localiza a seção manualmente
        inicio = c.find('<!-- GRÁFICO DE COMPOSIÇÃO -->')
        if inicio != -1:
            # Encontra o fechamento da .page correspondente (próximo </div> após o canvas e a tabela)
            # Vamos procurar o próximo <!-- CONCLUSÃO --> ou <!-- depois -->
            fim = c.find('<!-- CONCLUSÃO -->', inicio)
            if fim == -1:
                fim = c.find('<!--', inicio + 10)
            if fim != -1:
                c = c[:inicio] + novo_bloco + c[fim:]
                print("[OK] Layout ajustado manualmente!")
            else:
                print("[ERRO] Não foi possível encontrar o fim da seção.")

open('relatorio_final.html', 'w', encoding='utf-8').write(c)
print("[OK] relatorio_final.html atualizado!")
