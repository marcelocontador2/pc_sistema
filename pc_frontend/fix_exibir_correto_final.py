import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_exibir_correto_final")

# Encontra a funcao exibirSelecionado e substitui pela versao que busca a lista completa
padrao = re.compile(r'function exibirSelecionado\(\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match = padrao.search(s)

if match:
    nova_func = """function exibirSelecionado() {
    const check = document.querySelector('.check-hist:checked');
    if (!check) { alert("Selecione um item no histórico."); return; }
    const idProcurado = check.value;

    // Busca a LISTA completa (rota que existe no backend)
    fetch('/historico_composicao_receitas_despesas')
        .then(r => {
            if (!r.ok) throw new Error("HTTP " + r.status);
            return r.json();
        })
        .then(lista => {
            // Encontra o item com o ID selecionado
            const item = lista.find(i => String(i.id) === String(idProcurado));
            if (!item) { alert("Histórico não encontrado."); return; }

            let dados = item.resultado_json;
            if (typeof dados === 'string') {
                try { dados = JSON.parse(dados); } catch(e) { dados = null; }
            }
            if (!dados) { alert("Dados vazios."); return; }

            // A estrutura e: { atual: { receitas: {...}, despesas: {...} }, anterior: {...} }
            const d = dados;
            const atual = d.atual || {};
            const anterior = d.anterior || {};

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
    print("OK: Funcao exibirSelecionado corrigida para buscar a lista completa.")
else:
    print("ERRO: Funcao exibirSelecionado nao encontrada.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
