import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_comparativo_receitas_v2.html"

shutil.copy2(arquivo, f"{arquivo}.bak_fix_variavel_{ts}")
c = open(arquivo, encoding='utf-8').read()

# Localiza o bloco htmlGrupos
inicio = c.find('let htmlGrupos')
fim = c.find("document.getElementById('lista-grupos').innerHTML", inicio)

if inicio == -1 or fim == -1:
    print("[ERRO] Não encontrei o bloco htmlGrupos.")
    exit(1)

# Substitui o bloco inteiro por uma versão correta, com a variável definida
novo_bloco = """let htmlGrupos = '';
            gruposAt.forEach(function(g) {
                const valorAtual = g.realizado || 0;
                const anterior = (gruposAn.find(function(x) { return x.nome === g.nome; }) || {}).realizado || 0;
                const variacao = valorAtual - anterior;
                const pct = anterior > 0 ? (variacao / anterior) * 100 : 0;
                const cor = variacao >= 0 ? '#10b981' : '#dc2626';
                const seta = variacao >= 0 ? '▲' : '▼';
                
                // Valores completos (com pontos e vírgula)
                const txtAtual = 'R$ ' + fmt(valorAtual);
                const txtAnterior = anterior > 0 ? 'R$ ' + fmt(anterior) : '—';
                const txtVariacao = 'R$ ' + fmt(variacao);
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
            
            """

c = c[:inicio] + novo_bloco + c[fim:]

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Bloco corrigido: variavel valorAtual definida e formatacao completa!")
print("\n=== O QUE FOI CORRIGIDO ===")
print("1. Adicionada a definicao 'const valorAtual = g.realizado || 0;'")
print("2. Formatacao R$ XX.XXX.XXX,XX (com pontos e virgula)")
print("3. Variavel 'anterior' mantida correta")
print("4. 'txtPct' e 'txtVariacao' formatados corretamente")
