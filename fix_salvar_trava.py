import re
import shutil

caminho = "pc_frontend/analise_comparativo_receitas.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_fix_salvar_trava")

# Ajusta a função salvarAtual para remover a trava do dadosAtuais
nova_salvar = '''
function salvarAtual() {
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
                window.location.reload();
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
    print("✅ Trava removida. Botão Salvar vai funcionar independente do dadosAtuais.")
else:
    print("❌ Função salvarAtual() não encontrada.")

# Garante que a função verificar() atualiza o dadosAtuais
# Vamos procurar a função verificar() e verificar se tem o "dadosAtuais = data"
nova_verificar = '''
function verificar() {
    const ano = document.getElementById('ano').value;
    const tipo = document.getElementById('tipo').value;
    const valor = document.getElementById('valor').value;
    const periodo = `${ano}-${tipo}-${valor}`;

    const container = document.getElementById('tabela-container');
    container.innerHTML = '<div class="loading">Buscando dados...</div>';

    fetch(`/api/comparativo_receitas_v2/${periodo}?_t=${Date.now()}`)
        .then(res => res.json())
        .then(data => {
            if (data.erro) {
                alert("Aviso: " + data.mensagem);
                container.innerHTML = '';
                return;
            }
            dadosAtuais = data; // ISSO É CRUCIAL PARA O SALVAR FUNCIONAR
            atualizarCards(dadosAtuais);
            renderizarTabela(dadosAtuais);
        })
        .catch(err => {
            console.error(err);
            container.innerHTML = '<div class="loading">Erro ao buscar dados.</div>';
        });
}
'''

idx_inicio = html.find("function verificar()")
if idx_inicio != -1:
    i = html.find("{", idx_inicio)
    contador = 1
    i += 1
    while i < len(html) and contador > 0:
        if html[i] == "{": contador += 1
        elif html[i] == "}": contador -= 1
        i += 1
    html = html[:idx_inicio] + nova_verificar.strip() + html[i:]
    print("✅ Função verificar() atualizada para garantir que dadosAtuais seja preenchido.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Arquivo salvo.")
