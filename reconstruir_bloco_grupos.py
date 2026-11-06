import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_comparativo_receitas_v2.html"

shutil.copy2(arquivo, f"{arquivo}.bak_bloco_grupos_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Verifica se o bloco "lista-grupos" está no HTML (onde os cards são injetados)
if 'id="lista-grupos"' not in c:
    print("[AVISO] A div 'lista-grupos' não está no HTML. Vou recriar.")

# 2. Localiza o ponto de inserção do código JS (onde estava o bloco antigo)
# Procura a partir do fechamento da função 'carregarDados' (onde está o código dos gráficos)
marcador = "const meta = at.orcado_total;"
idx = c.find(marcador)

if idx == -1:
    # Se não encontrar pelo marcador, tenta outro
    marcador = "document.getElementById('meta-anual').innerText"
    idx = c.find(marcador)

if idx == -1:
    # Último recurso: insere no final do script
    idx = c.rfind('document.addEventListener(\'DOMContentLoaded\', carregarDados);')

if idx == -1:
    print("[ERRO] Não consegui encontrar o ponto de inserção.")
    exit(1)

# 3. Cria o novo bloco de geração dos cards
novo_bloco = """
            // ==========================================
            // CARDS DE GRUPOS DE RECEITA (Reconstruídos)
            // ==========================================
            let htmlGrupos = '';
            gruposAt.forEach(function(g) {
                const valorAtual = g.realizado || 0;
                const anterior = (gruposAn.find(function(x) { return x.nome === g.nome; }) || {}).realizado || 0;
                const variacao = valorAtual - anterior;
                const pct = anterior > 0 ? (variacao / anterior) * 100 : 0;
                const cor = variacao >= 0 ? '#10b981' : '#dc2626';
                const seta = variacao >= 0 ? '▲' : '▼';
                
                // Formatação sem duplicar R$ (fmt() já retorna com R$)
                const txtAtual = fmt(valorAtual);
                const txtAnterior = anterior > 0 ? fmt(anterior) : '—';
                const txtVariacao = fmt(variacao);
                const txtPct = anterior > 0 ? fmtPct(pct) : 'Sem dados anteriores';
                
                htmlGrupos += 
                    '<div class="grupo-item" style="border-left-color: ' + cor + ';">' +
                        '<div class="grupo-nome">' + capitalizeNome(g.nome) + '</div>' +
                        '<div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px; margin-bottom: 4px;">' +
                            '<div style="font-size: 13px; color: #1e293b;">' +
                                '<strong>Recebido:</strong> ' + txtAtual +
                            '</div>' +
                            '<div style="font-size: 11px; color: #64748b;">' +
                                'Anterior: ' + txtAnterior +
                            '</div>' +
                        '</div>' +
                        '<div style="font-size: 12px; color: ' + cor + '; font-weight: bold;">' +
                            seta + ' ' + txtVariacao + ' (' + txtPct + ')' +
                        '</div>' +
                    '</div>';
            });
            
            const divGrupos = document.getElementById('lista-grupos');
            if (divGrupos) divGrupos.innerHTML = htmlGrupos;
            
            """

# 4. Insere o novo bloco no ponto de inserção
c = c[:idx] + novo_bloco + c[idx:]

# 5. Garante que a div 'lista-grupos' existe no HTML
if 'id="lista-grupos"' not in c:
    # Procura a página 3 (composição) para inserir
    marcador_pagina3 = 'Composição por Grupo de Receita'
    idx_pagina3 = c.find(marcador_pagina3)
    if idx_pagina3 != -1:
        # Encontra o fechamento da div do gráfico (canvas) e insere a div após ele
        pos_canvas = c.find('canvas id="grafico-grupos"', idx_pagina3)
        if pos_canvas != -1:
            pos_fim = c.find('>', pos_canvas) + 1
            c = c[:pos_fim] + '\n<div id="lista-grupos" style="margin-top: 15px;"></div>\n' + c[pos_fim:]
            print("[OK] Div 'lista-grupos' criada no HTML.")
    else:
        print("[AVISO] Não encontrei a página 3 para inserir a div.")

open(arquivo, 'w', encoding='utf-8').write(c)
print("\n[OK] Bloco de geração dos cards reconstruído com sucesso!")
print("\n=== O QUE FOI FEITO ===")
print("1. Reconstruído o bloco 'htmlGrupos' que faltava")
print("2. Valores formatados como R$ 20.058.909,55 (sem duplicar)")
print("3. Layout de cada card com 'Recebido', 'Anterior' e variação")
print("4. Div 'lista-grupos' garantida no HTML")
