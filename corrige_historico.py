import sys
from pathlib import Path
import re

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_frontend/relatorio_consolidado.html")
texto = arquivo.read_text(encoding="utf-8")

# 1. Substituir a funcao carregarHistorico inteira por uma versao limpa e correta
padrao = re.compile(r'function carregarHistorico\(\)\s*\{.*?\n\s*\}', re.DOTALL)
nova_funcao = '''function carregarHistorico() {
            const lista = document.getElementById('lista-historico');
            if (!lista) return;
            lista.innerHTML = '<li>Carregando...</li>';
            
            fetch('/historico_relatorio_consolidado')
                .then(r => r.json())
                .then(data => {
                    if (data && data.length > 0) {
                        lista.innerHTML = data.map(function(h) {
                            return '<li><input type="checkbox" class="checkbox-historico" value="' + h.id + '" onchange="atualizarBotaoExcluir()"><span>Período: ' + h.periodo + '<br><small style="color: #999;">' + (h.data_geracao || 'N/A') + '</small></span></li>';
                        }).join('');
                    } else {
                        lista.innerHTML = '<li style="color: #666;">Nenhum histórico salvo.</li>';
                    }
                    atualizarBotaoExcluir();
                })
                .catch(e => {
                    lista.innerHTML = '<li style="color: red;">Erro ao carregar histórico: ' + e + '</li>';
                });
        }'''

if padrao.search(texto):
    texto = padrao.sub(nova_funcao, texto, count=1)
    print("[OK] Funcao carregarHistorico reescrita.")
else:
    print("[AVISO] Nao encontrei a funcao carregarHistorico para substituir.")

# 2. Garantir que o window.onload chame carregarHistorico e atualizarBotaoExcluir
if "window.onload = function() { carregarHistorico(); };" not in texto:
    if "window.onload" in texto:
        # Se ja existe, sobrescreve
        texto = re.sub(r'window\.onload\s*=\s*function\(\)\s*\{.*?\};', 'window.onload = function() { carregarHistorico(); atualizarBotaoExcluir(); };', texto, flags=re.DOTALL)
        print("[OK] window.onload atualizado.")
    else:
        pos = texto.rfind('</script>')
        if pos != -1:
            texto = texto[:pos] + '\n    window.onload = function() { carregarHistorico(); atualizarBotaoExcluir(); };\n' + texto[pos:]
            print("[OK] window.onload adicionado.")
else:
    print("[INFO] window.onload ja esta correto.")

arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo salvo.")
