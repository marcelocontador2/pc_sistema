import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_exibir_final_fix")

# Encontra a funcao exibirSelecionado e substitui pela versao corrigida
padrao = re.compile(r'function exibirSelecionado\(\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match = padrao.search(s)

if match:
    nova_func = """function exibirSelecionado() {
    const check = document.querySelector('.check-hist:checked');
    if (!check) { alert("Selecione um item no histórico."); return; }
    const idProcurado = check.value;

    // Busca o historico com ID (rota que retorna o JSON com atual e anterior)
    fetch('/historico_composicao_receitas_despesas/' + idProcurado)
        .then(r => {
            if (!r.ok) throw new Error("HTTP " + r.status);
            return r.json();
        })
        .then(dados => {
            if (!dados) { alert("Dados vazios."); return; }

            // A API retorna { periodo, periodo_anterior, atual: { receitas, despesas }, anterior: {...} }
            // O objeto raiz JA E o "dados", entao acessamos diretamente .atual e .anterior
            const atual = dados.atual || {};
            const anterior = dados.anterior || {};

            // Renderiza as tabelas
            if (typeof renderTabela === 'function') {
                renderTabela('tab-receitas', atual.receitas, anterior.receitas);
                renderTabela('tab-despesas', atual.despesas, anterior.despesas);
            }

            // Renderiza o grafico
            if (typeof renderChart === 'function') {
                renderChart({receitas: atual.receitas}, {receitas: anterior.receitas});
            }
        })
        .catch(e => {
            alert("Erro ao carregar o histórico: " + e.message);
            console.error(e);
        });
}
"""
    s = s[:match.start()] + nova_func + s[match.end():]
    print("OK: Funcao exibirSelecionado corrigida para acessar diretamente .atual e .anterior.")
else:
    print("ERRO: Funcao exibirSelecionado nao encontrada.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
