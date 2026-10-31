from pathlib import Path
import re

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Corrigir o visual dos botoes (mudar a cor de fundo via JS e remover o inline)
# Remover o style inline dos botoes (para o JS controlar)
conteudo = re.sub(
    r'<button type="button" id="btn-cofen"[^>]*>',
    '<button type="button" id="btn-cofen" style="padding: 10px 20px; border: none; cursor: pointer; font-weight: bold;">',
    conteudo
)
conteudo = re.sub(
    r'<button type="button" id="btn-coren"[^>]*>',
    '<button type="button" id="btn-coren" style="padding: 10px 20px; border: none; cursor: pointer; font-weight: bold;">',
    conteudo
)

# 2. Atualizar a funcao mudarEntidade para usar classList (mais confiavel)
# E atualizar o window.onload para usar classList tambem
novo_js_botoes = '''
        function atualizarVisualBotoes(entidade) {
            var btnCofen = document.getElementById('btn-cofen');
            var btnCoren = document.getElementById('btn-coren');
            if (btnCofen) {
                if (entidade === 'COFEN') {
                    btnCofen.style.background = '#003366';
                    btnCofen.style.color = '#fff';
                } else {
                    btnCofen.style.background = '#f0f0f0';
                    btnCofen.style.color = '#333';
                }
            }
            if (btnCoren) {
                if (entidade === 'COREN') {
                    btnCoren.style.background = '#003366';
                    btnCoren.style.color = '#fff';
                } else {
                    btnCoren.style.background = '#f0f0f0';
                    btnCoren.style.color = '#333';
                }
            }
        }
'''

# Adicionar a funcao atualizarVisualBotoes antes de mudarEntidade
if "function atualizarVisualBotoes" not in conteudo:
    trecho = "function mudarEntidade(novaEntidade)"
    if trecho in conteudo:
        conteudo = conteudo.replace(trecho, novo_js_botoes + "\n        " + trecho, 1)
        print("OK: Funcao atualizarVisualBotoes adicionada!")

# 3. Substituir o corpo do mudarEntidade para usar atualizarVisualBotoes
padrao_mudar = r"function mudarEntidade\(novaEntidade\) \{.*?\n        \}"
novo_mudar = '''function mudarEntidade(novaEntidade) {
            console.log("[TOGGLE] Mudando para:", novaEntidade);
            atualizarVisualBotoes(novaEntidade);
            
            fetch('/api/configuracoes', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({tipo_entidade: novaEntidade})
            })
            .then(r => r.json())
            .then(function(d) {
                console.log("[TOGGLE] Salvo:", d);
                setTimeout(carregar, 300);
            })
            .catch(function(e) { console.error("[TOGGLE] Erro:", e); });
        }'''

match = re.search(padrao_mudar, conteudo, re.DOTALL)
if match:
    conteudo = conteudo.replace(match.group(0), novo_mudar, 1)
    print("OK: mudarEntidade atualizado!")

# 4. Corrigir o window.onload para usar atualizarVisualBotoes
padrao_onload = r"window\.onload = function\(\) \{.*?\n        \};"
novo_onload = '''window.onload = function() {
            carregar();
            fetch('/api/configuracoes').then(r => r.json()).then(function(d) {
                var ent = d.tipo_entidade || 'COFEN';
                atualizarVisualBotoes(ent);
            }).catch(function(e) { console.error(e); });
        };'''

match = re.search(padrao_onload, conteudo, re.DOTALL)
if match:
    conteudo = conteudo.replace(match.group(0), novo_onload, 1)
    print("OK: window.onload atualizado!")

# 5. Corrigir o Historico Salvo (adicionar o fetch que faltava)
if "carregarHistorico" not in conteudo:
    # Adicionar chamada do historico no onload
    conteudo = conteudo.replace(
        "window.onload = function() {\n            carregar();",
        "window.onload = function() {\n            carregar();\n            carregarHistorico();"
    )
    # Adicionar a funcao carregarHistorico
    funcao_hist = '''
        function carregarHistorico() {
            fetch('/historico_custo_pessoal')
                .then(r => r.json())
                .then(function(data) {
                    var div = document.getElementById('historico');
                    if (!div) return;
                    if (!data || data.length === 0) {
                        div.innerHTML = '<p style="color:#666;">Nenhum histórico salvo.</p>';
                        return;
                    }
                    var html = '';
                    data.forEach(function(item) {
                        html += '<div style="padding:10px; border-bottom:1px solid #eee; cursor:pointer;" onclick="exibirHistorico(' + item.id + ')">';
                        html += '<b>' + item.periodo + '</b><br>';
                        html += '<small style="color:#666;">' + item.data_geracao + '</small>';
                        html += '</div>';
                    });
                    div.innerHTML = html;
                })
                .catch(function(e) { console.error('Erro ao carregar historico:', e); });
        }
        
        function exibirHistorico(id) {
            fetch('/historico_custo_pessoal/' + id)
                .then(r => r.json())
                .then(function(d) {
                    if (d.dados) preencherTabela(d.dados);
                });
        }
        
        '''
    # Adicionar antes do window.onload
    conteudo = conteudo.replace("window.onload = function() {", funcao_hist + "window.onload = function() {", 1)
    print("OK: Funcao carregarHistorico adicionada!")

# 6. Corrigir o "Carregando..." (adicionar id no HTML)
if 'id="historico"' not in conteudo:
    conteudo = conteudo.replace(
        '<h3>Histórico Salvo</h3>',
        '<h3>Histórico Salvo</h3><div id="historico"><p style="color:#666;">Carregando...</p></div>'
    )
    print("OK: div do historico adicionada!")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: HTML atualizado!")
