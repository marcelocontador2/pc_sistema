import re
import shutil

caminho = "pc_frontend/analise_comparativo_despesas.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_verificar_exibir_despesas")

# --- 1. Substituir função verificar() ---
nova_verificar = '''
function verificar() {
    const ano = document.getElementById('ano').value;
    const tipo = document.getElementById('tipo').value;
    const valor = document.getElementById('valor').value;
    const periodo = `${ano}-${tipo}-${valor}`;

    const container = document.getElementById('tabela-container');
    if (container) container.innerHTML = '<div class="loading">Buscando dados...</div>';

    fetch(`/api/comparativo_despesas_v2/${periodo}?_t=${Date.now()}`)
        .then(res => res.json())
        .then(data => {
            if (data.erro) {
                alert("Aviso: " + data.mensagem);
                if (container) container.innerHTML = '';
                return;
            }
            dadosAtuais = data;
            atualizarCards(data);
            renderizarTabela(data);
        })
        .catch(err => {
            console.error(err);
            if (container) container.innerHTML = '<div class="loading">Erro ao buscar dados.</div>';
        });
}
'''

# --- 2. Substituir função exibirSelecionado() ---
nova_exibir = '''
function exibirSelecionado() {
    const id = getHistoricoSelecionado();
    if (!id) { alert("Selecione um histórico na lista."); return; }

    fetch(`/historico_comparativo_despesas/${id}`)
        .then(res => res.json())
        .then(data => {
            if (data.erro) { alert("Erro: " + data.mensagem); return; }

            // O histórico pode vir como {dados: ...} ou direto
            let payload = data.dados ? data.dados : data;

            // Se o payload for string JSON, converte
            if (typeof payload === 'string') {
                try { payload = JSON.parse(payload); } catch(e) {}
            }

            // Se o payload for um objeto que tem "atual", usa direto
            if (payload && payload.atual) {
                dadosAtuais = payload;
            } else if (payload && payload.empenhado_total !== undefined) {
                // Se for o objeto "atual" direto, envelopa
                dadosAtuais = { atual: payload, anterior: null };
            } else {
                dadosAtuais = payload;
            }

            atualizarCards(dadosAtuais);
            renderizarTabela(dadosAtuais);
        })
        .catch(err => alert("Erro ao carregar histórico: " + err));
}
'''

# Substitui as funções no HTML
for nome_func, nova in [("verificar", nova_verificar), ("exibirSelecionado", nova_exibir)]:
    idx = html.find(f"function {nome_func}(")
    if idx != -1:
        i = html.find("{", idx)
        contador = 1
        i += 1
        while i < len(html) and contador > 0:
            if html[i] == "{": contador += 1
            elif html[i] == "}": contador -= 1
            i += 1
        html = html[:idx] + nova.strip() + html[i:]
        print(f"✅ Função {nome_func}() substituída.")
    else:
        # Se não existir, cria antes do </script>
        html = html.replace("</script>", nova + "\n</script>")
        print(f"✅ Função {nome_func}() criada.")

# --- 3. Garantir que atualizarCards() use "atual" ---
nova_cards = '''
function atualizarCards(data) {
    const atual = (data && data.atual) ? data.atual : (data || {});
    const anterior = (data && data.anterior) ? data.anterior : {};

    const cardEmp = document.getElementById('card-realizado') || document.getElementById('card-empenhado');
    if (cardEmp) cardEmp.innerText = formatarMoeda(atual.empenhado_total);

    const cardOrc = document.getElementById('card-orcado');
    if (cardOrc) cardOrc.innerText = formatarMoeda(atual.orcado_total);

    const cardPct = document.getElementById('card-percentual');
    if (cardPct) cardPct.innerText = (atual.percentual_total || 0).toFixed(2) + '%';
}
'''
idx_cards = html.find("function atualizarCards(")
if idx_cards != -1:
    i = html.find("{", idx_cards)
    contador = 1
    i += 1
    while i < len(html) and contador > 0:
        if html[i] == "{": contador += 1
        elif html[i] == "}": contador -= 1
        i += 1
    html = html[:idx_cards] + nova_cards.strip() + html[i:]
    print("✅ Função atualizarCards() ajustada para 'atual'.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ Arquivo HTML salvo.")
