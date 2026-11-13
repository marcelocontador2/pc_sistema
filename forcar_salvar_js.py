import re

caminho = "pc_frontend/integridade.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

# Localiza a função salvarMatriz (seja async ou não)
idx_inicio = html.find("async function salvarMatriz(")
if idx_inicio == -1:
    idx_inicio = html.find("function salvarMatriz(")

if idx_inicio != -1:
    # Encontra o fechamento da função (conta as chaves)
    i = html.find("{", idx_inicio)
    contador = 1
    i += 1
    while i < len(html) and contador > 0:
        if html[i] == "{": contador += 1
        elif html[i] == "}": contador -= 1
        i += 1
    
    # Substitui pela versão definitiva
    nova_funcao = '''async function salvarMatriz() {
        const ano = document.getElementById('ano').value;
        const tipo = document.getElementById('tipo_periodo').value;
        const trimestre = document.getElementById('trimestre').value;
        const periodo = `${ano}-${tipo}-${trimestre}`;

        if (!dadosAtuais || !dadosAtuais.matriz) {
            alert("Nenhuma matriz carregada para salvar. Clique em 'Verificar Matriz' primeiro.");
            return;
        }

        if (!confirm("Deseja realmente salvar esta matriz no histórico?")) return;

        try {
            const res = await fetch(`/api/integridade_matriz/${periodo}/salvar`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    matriz: dadosAtuais.matriz,
                    justificativas: dadosAtuais.justificativas || {}
                })
            });
            
            const data = await res.json();
            if (data.erro) {
                alert("Erro ao salvar: " + data.mensagem);
            } else {
                alert("Matriz salva com sucesso no PostgreSQL!");
                await carregarHistorico(); // Atualiza a lista lateral
            }
        } catch (err) {
            alert("Erro de conexão ao salvar: " + err.message);
        }
    }'''
    
    html = html[:idx_inicio] + nova_funcao + html[i:]
    
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Função 'salvarMatriz' substituída com sucesso pela versão definitiva!")
else:
    print("❌ Função 'salvarMatriz' não foi encontrada no arquivo para substituir.")
