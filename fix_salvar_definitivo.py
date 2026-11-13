import re
import shutil

caminho = "pc_frontend/analise_comparativo_receitas.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_fix_salvar_definitivo")

# 1. Substitui a função salvarAtual por uma versão que força a atualização
nova_salvar = '''
function salvarAtual() {
    alert("Botão salvar clicado!"); // TESTE
    
    if (!dadosAtuais) { 
        alert("Verifique os dados primeiro."); 
        return; 
    }
    
    const ano = document.getElementById('ano').value;
    const tipo = document.getElementById('tipo').value;
    const valor = document.getElementById('valor').value;
    const periodo = `${ano}-${tipo}-${valor}`;
    
    fetch(`/api/comparativo_receitas_v2/${periodo}/salvar`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.erro) {
                alert("Erro: " + data.mensagem);
            } else {
                alert("Salvo com sucesso!");
                // Recarrega a lista diretamente
                carregarHistorico();
            }
        })
        .catch(err => alert("Erro ao salvar: " + err));
}
'''

idx_inicio = html.find("function salvarAtual()")
if idx_inicio != -1:
    i = html.find("{", idx_inicio)
    contador = 1
    i += 1
    while i < len(html) and contador > 0:
        if html[i] == "{": contador += 1
        elif html[i] == "}": contador -= 1
        i += 1
    html = html[:idx_inicio] + nova_salvar.strip() + html[i:]
    print("✅ Função salvarAtual() substituída com alert de teste.")

# 2. Substitui a função carregarHistorico por uma versão que NÃO usa template strings complexas
nova_historico = '''
function carregarHistorico() {
    console.log("[TESTE] carregarHistorico() chamada");
    const list = document.getElementById('historico-lista');
    if (!list) {
        alert("ERRO: Container 'historico-lista' não encontrado!");
        return;
    }
    
    list.innerHTML = '<li>Carregando...</li>';
    
    fetch('/historico_comparativo_receitas?_t=' + Date.now())
        .then(res => res.json())
        .then(data => {
            console.log("[TESTE] Históricos:", data);
            list.innerHTML = '';
            
            if (data && data.length > 0) {
                for (let i = 0; i < data.length; i++) {
                    const h = data[i];
                    const li = document.createElement('li');
                    const cb = document.createElement('input');
                    cb.type = 'checkbox';
                    cb.value = h.id;
                    const span = document.createElement('span');
                    span.textContent = 'Período: ' + h.periodo + ' | Gerado em: ' + (h.data_geracao || h.criado_em || 'N/A');
                    li.appendChild(cb);
                    li.appendChild(span);
                    list.appendChild(li);
                }
                console.log("[TESTE] Lista atualizada com " + data.length + " itens");
            } else {
                list.innerHTML = '<li>Nenhum histórico salvo.</li>';
            }
        })
        .catch(err => {
            alert("ERRO no carregarHistorico: " + err);
        });
}
'''

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
    print("✅ Função carregarHistorico() substituída por versão síncrona.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Arquivo salvo.")
