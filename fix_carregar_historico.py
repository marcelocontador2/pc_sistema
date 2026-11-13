import re
import shutil

caminho = "pc_frontend/analise_comparativo_receitas.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_fix_carregar_historico")

# Substitui a função carregarHistorico por uma versão robusta
nova_historico = '''
function carregarHistorico() {
    console.log("[DEBUG] carregarHistorico() chamado");
    const list = document.getElementById('historico-lista');
    if (!list) {
        console.error("[DEBUG] Container 'historico-lista' não encontrado!");
        return;
    }
    
    list.innerHTML = '<li class="loading">Carregando histórico...</li>';
    
    fetch(`/historico_comparativo_receitas?_t=${Date.now()}`)
        .then(res => {
            console.log("[DEBUG] Status do carregarHistorico:", res.status);
            if (!res.ok) throw new Error("HTTP " + res.status);
            return res.json();
        })
        .then(data => {
            console.log("[DEBUG] Históricos recebidos:", data.length);
            list.innerHTML = '';
            
            if (data && data.length > 0) {
                data.forEach(h => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <input type="checkbox" value="${h.id}">
                        <span>Período: ${h.periodo} | Gerado em: ${h.data_geracao || h.criado_em || 'N/A'}</span>
                    `;
                    list.appendChild(li);
                });
                console.log("[DEBUG] Lista atualizada com", data.length, "itens");
            } else {
                list.innerHTML = '<li>Nenhum histórico salvo.</li>';
            }
        })
        .catch(err => {
            console.error("[DEBUG] ERRO no carregarHistorico:", err);
            list.innerHTML = '<li>Erro ao carregar histórico.</li>';
        });
}
'''

# Localiza e substitui a função carregarHistorico
idx_inicio = html.find("function carregarHistorico()")
if idx_inicio != -1:
    i = html.find("{", idx_inicio)
    contador = 1
    i += 1
    while i < len(html) and contador > 0:
        if html[i] == "{": contador += 1
        elif html[i] == "}": contador -= 1
        i += 1
    html = html[:idx_inicio] + nova_historico.strip() + html[i:]
    print("✅ Função carregarHistorico() substituída por versão robusta.")
else:
    print("❌ Função carregarHistorico() não encontrada.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Arquivo salvo.")
