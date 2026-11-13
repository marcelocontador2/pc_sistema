import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_hist_fix")

# 1) Encontra a funcao salvarComposicao() e garante que ela chame carregarHistorico()
padrao = re.compile(r'function salvarComposicao\(\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match = padrao.search(s)

if match:
    nova_func = """function salvarComposicao() {
    const ano = document.getElementById('ano_atual').value;
    const tipo = document.getElementById('tipo_atual').value;
    const val = document.getElementById('val_atual').value;
    const periodo = ano + '-' + tipo + '-' + val;
    
    const ano_ant = document.getElementById('ano_anterior') ? document.getElementById('ano_anterior').value : ano;
    const tipo_ant = document.getElementById('tipo_anterior') ? document.getElementById('tipo_anterior').value : tipo;
    const val_ant = document.getElementById('val_anterior') ? document.getElementById('val_anterior').value : val;
    const periodo_anterior = ano_ant + '-' + tipo_ant + '-' + val_ant;

    fetch('/salvar_composicao_receitas_despesas/' + periodo + '/' + periodo_anterior, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.mensagem === "Salvo" || data.ok) {
                alert("Relatório salvo com sucesso!");
                carregarHistorico();
            } else {
                alert("Erro: " + (data.mensagem || "Erro desconhecido"));
            }
        })
        .catch(e => alert("Erro de conexão: " + e.message));
}
"""
    s = s[:match.start()] + nova_func + s[match.end():]
    print("OK: Funcao salvarComposicao() corrigida para chamar carregarHistorico().")
else:
    print("AVISO: Funcao salvarComposicao() nao encontrada.")

# 2) Garante que a funcao carregarHistorico() exista e esteja funcionando
padrao_hist = re.compile(r'function carregarHistorico\(\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match_hist = padrao_hist.search(s)

if match_hist:
    nova_hist = """function carregarHistorico() {
    fetch('/historico_composicao_receitas_despesas')
        .then(r => r.json())
        .then(data => {
            const lista = document.getElementById('historico-lista');
            if (!lista) return;
            
            if (!data || data.length === 0) {
                lista.innerHTML = 'Nenhum histórico.';
                return;
            }
            
            let html = '';
            data.forEach(item => {
                html += `<div class="hist-item" style="margin-bottom: 8px; border-bottom: 1px solid #eee; padding-bottom: 4px; display: flex; align-items: center; gap: 8px;">
                    <input type="checkbox" class="check-hist" value="${item.id}">
                    <div>
                        <strong>${item.periodo}</strong><br>
                        <span style="font-size: 11px; color: #888;">${item.data_geracao}</span>
                    </div>
                </div>`;
            });
            lista.innerHTML = html;
        })
        .catch(e => {
            console.error("Erro ao carregar histórico:", e);
            const lista = document.getElementById('historico-lista');
            if (lista) lista.innerHTML = 'Erro ao carregar.';
        });
}
"""
    s = s[:match_hist.start()] + nova_hist + s[match_hist.end():]
    print("OK: Funcao carregarHistorico() corrigida.")
else:
    print("AVISO: Funcao carregarHistorico() nao encontrada.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
