import shutil

caminho = "pc_frontend/integridade.html"
shutil.copy(caminho, caminho + ".bak_fix_salvar_js")

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

# Verifica se a função já foi adicionada
if "function salvarMatriz(" not in html and "async function salvarMatriz(" not in html:
    # Procura o fechamento da tag <script>
    idx_fim_script = html.rfind("</script>")
    
    if idx_fim_script != -1:
        funcao_salvar = '''
    async function salvarMatriz() {
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
                carregarHistorico(); // Atualiza a lista lateral
            }
        } catch (err) {
            alert("Erro de conexão ao salvar: " + err.message);
        }
    }
'''
        # Insere a função antes do fechamento do script
        html = html[:idx_fim_script] + funcao_salvar + html[idx_fim_script:]
        
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ Função JavaScript 'salvarMatriz' adicionada com sucesso!")
    else:
        print("❌ Tag </script> não encontrada no HTML.")
else:
    print("✅ Função 'salvarMatriz' já existe no arquivo. Nada a fazer.")
