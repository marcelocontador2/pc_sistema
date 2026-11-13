import re
import shutil

caminho = "pc_frontend/analise_comparativo_receitas.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_fix_exibir")

# Substitui a função exibirSelecionado
nova_exibir = '''
function exibirSelecionado() {
    const id = getHistoricoSelecionado();
    if (!id) { alert("Selecione um histórico na lista."); return; }
    
    // Em vez de confiar no JSON salvo no banco (que pode estar velho),
    // vamos buscar o histórico apenas para pegar o PERÍODO, e depois forçar o recálculo do CSV.
    fetch(`/historico_comparativo_receitas/${id}`)
        .then(res => res.json())
        .then(data => {
            if (data.erro) { alert("Erro: " + data.mensagem); return; }
            
            // Tenta extrair o período do histórico (pode estar em data.periodo, data.dados.periodo, etc)
            const periodo = data.periodo || (data.dados && data.dados.periodo);
            
            if (periodo) {
                // Atualiza os selects da tela para refletir o período do histórico
                const partes = periodo.split("-");
                if (partes.length === 3) {
                    document.getElementById('ano').value = partes[0];
                    document.getElementById('tipo').value = partes[1];
                    document.getElementById('valor').value = partes[2];
                }
                // Chama a função verificar() que busca os dados frescos do CSV
                verificar();
            } else {
                // Se não achou o período no histórico, tenta usar os dados salvos
                const payload = data.dados ? data.dados : data;
                dadosAtuais = payload;
                atualizarCards(dadosAtuais);
                renderizarTabela(dadosAtuais);
            }
        })
        .catch(err => alert("Erro ao carregar histórico: " + err));
}
'''

# Localiza e substitui a função exibirSelecionado
idx_inicio = html.find("function exibirSelecionado()")
if idx_inicio != -1:
    i = html.find("{", idx_inicio)
    contador = 1
    i += 1
    while i < len(html) and contador > 0:
        if html[i] == "{": contador += 1
        elif html[i] == "}": contador -= 1
        i += 1
    html = html[:idx_inicio] + nova_exibir.strip() + html[i:]
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Função exibirSelecionado() atualizada para forçar o recálculo do CSV.")
else:
    print("❌ Função exibirSelecionado() não encontrada.")
