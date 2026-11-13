import re
import shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_reescrever_js")

# 1. Remove as funcoes antigas que podem estar causando conflito
# Removemos as funcoes carregarHistorico, exibirSelecionado e salvarComposicao
for func_name in ["carregarHistorico", "exibirSelecionado", "salvarComposicao"]:
    padrao = re.compile(r'function\s+' + func_name + r'\s*\([^)]*\)\s*\{.*?\n\}', re.DOTALL)
    s = padrao.sub('', s)

# 2. Remove os event listeners antigos do DOMContentLoaded
s = re.sub(r'document\.addEventListener\(\'DOMContentLoaded\'.*?\}\);', '', s, flags=re.DOTALL)

# 3. Cria o novo bloco de JavaScript limpo
novo_js = '''
<script>
// ========== FUNCOES DA COMPOSICAO ==========

function carregarHistorico() {
    fetch('/historico_composicao_receitas_despesas')
        .then(r => r.json())
        .then(data => {
            const el = document.getElementById('historico-lista');
            if (!el) return;
            if (!data || data.length === 0) { el.innerHTML = '<li>Nenhum histórico.</li>'; return; }
            let html = '';
            data.forEach(item => {
                html += `<li>
                    <label>
                        <input type="checkbox" class="check-hist" value="${item.id}" style="margin-right:5px;">
                        <strong>${item.periodo}</strong><br>
                        <small style="color:#666;">${item.data_geracao}</small>
                    </label>
                </li>`;
            });
            el.innerHTML = html;
        })
        .catch(e => {
            console.error("Erro ao carregar historico:", e);
            const el = document.getElementById('historico-lista');
            if (el) el.innerHTML = '<li>Erro ao carregar.</li>';
        });
}

function exibirSelecionado() {
    const check = document.querySelector('.check-hist:checked');
    if (!check) { alert("Selecione um item no histórico."); return; }
    
    const id = check.value;
    
    fetch('/historico_composicao_receitas_despesas/' + id)
        .then(r => {
            if (!r.ok) throw new Error("HTTP " + r.status);
            return r.json();
        })
        .then(dados => {
            if (!dados) { alert("Dados vazios."); return; }
            
            // A API retorna o objeto com .atual e .anterior
            const atual = dados.atual || {};
            const anterior = dados.anterior || {};
            
            // Renderiza tabelas
            if (atual.receitas && anterior.receitas) {
                renderTabela('tab-receitas', atual.receitas, anterior.receitas);
            }
            if (atual.despesas && anterior.despesas) {
                renderTabela('tab-despesas', atual.despesas, anterior.despesas);
            }
            
            // Renderiza grafico
            if (typeof renderChart === 'function') {
                renderChart(atual, anterior);
            }
        })
        .catch(e => {
            alert("Erro ao carregar histórico: " + e.message);
            console.error(e);
        });
}

function salvarComposicao() {
    const ano = document.getElementById('ano_atual').value;
    const tipo = document.getElementById('tipo_atual').value;
    const val = document.getElementById('val_atual').value;
    
    // Monta o periodo atual e o anterior
    const pAtual = ano + '-' + tipo + '-' + val;
    const pAnterior = String(parseInt(ano) - 1) + '-' + tipo + '-' + val;
    
    fetch('/salvar_composicao_receitas_despesas/' + pAtual + '/' + pAnterior, { method: 'POST' })
        .then(r => {
            if (!r.ok) throw new Error("HTTP " + r.status);
            return r.json();
        })
        .then(res => {
            alert("Relatório salvo com sucesso!");
            carregarHistorico(); // Atualiza a lista lateral
        })
        .catch(e => {
            alert("Erro ao salvar: " + e.message);
            console.error(e);
        });
}

// ========== INICIALIZACAO ==========
document.addEventListener("DOMContentLoaded", function() {
    carregarHistorico();
    
    // Vincula o botao Exibir
    const btnExibir = document.getElementById('btn-exibir-composicao');
    if (btnExibir) btnExibir.addEventListener('click', exibirSelecionado);
    
    // Vincula o botao Confirmar e Salvar
    const btnSalvar = document.querySelector('button[onclick="salvarComposicao()"]');
    if (btnSalvar) {
        btnSalvar.removeAttribute('onclick'); // remove o antigo
        btnSalvar.addEventListener('click', salvarComposicao);
    }
});
</script>
'''

# 4. Injeta o novo JS antes do </body>
if "</body>" in s:
    s = s.replace("</body>", novo_js + "\n</body>")
else:
    s += novo_js

with open(path, "w", encoding="utf-8") as f:
    f.write(s)

print("OK: JavaScript da Composicao reescrito do zero e botoes reconectados!")
