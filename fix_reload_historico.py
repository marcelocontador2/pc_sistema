import re
import shutil

caminho = "pc_frontend/analise_comparativo_receitas.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_reload_historico")

# Substitui a função salvarAtual por uma versão que recarrega a página inteira
nova_salvar = '''
function salvarAtual() {
    if (!dadosAtuais) { alert("Verifique os dados primeiro."); return; }
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
                // Força o recarregamento completo da página
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
    print("✅ Função salvarAtual() atualizada para recarregar a página.")
else:
    print("❌ Função salvarAtual() não encontrada.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Arquivo salvo.")
