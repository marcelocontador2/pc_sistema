import shutil

caminho = "pc_frontend/relatorio_consolidado.html"
shutil.copy(caminho, caminho + ".bak_add_botao_salvar")

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Adicionar o botão HTML "Confirmar e Salvar" (ao lado do Gerar PDF)
if 'id="btn-salvar-consolidado"' not in html:
    idx_btn = html.find('Gerar PDF</button>')
    if idx_btn != -1:
        fim_btn = html.find('>', idx_btn) + 1
        botao_novo = '\n            <button id="btn-salvar-consolidado" class="btn btn-success" onclick="salvarRelatorioConsolidado()" style="margin-left: 10px; background-color: #198754; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; font-weight: bold;">Confirmar e Salvar</button>'
        html = html[:fim_btn] + botao_novo + html[fim_btn:]
        print("✅ Botão HTML 'Confirmar e Salvar' adicionado.")

# 2. Adicionar a função salvarRelatorioConsolidado() se não existir
if "function salvarRelatorioConsolidado(" not in html and "async function salvarRelatorioConsolidado(" not in html:
    idx_fim_script = html.rfind("</script>")
    if idx_fim_script != -1:
        funcao_salvar = '''
    async function salvarRelatorioConsolidado() {
        const ano = document.getElementById('ano').value;
        const tipo = document.getElementById('tipo_periodo').value;
        const trimestre = document.getElementById('trimestre').value;
        const periodo = `${ano}-${tipo}-${trimestre}`;

        if (!confirm("Deseja realmente salvar este relatório consolidado no histórico?")) return;

        try {
            const res = await fetch(`/salvar_relatorio_consolidado/${periodo}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await res.json();
            if (data.ok) {
                alert("Relatório salvo com sucesso no PostgreSQL!");
                // Recarrega a lista lateral
                if (typeof carregarHistorico === 'function') {
                    carregarHistorico();
                } else {
                    window.location.reload();
                }
            } else {
                alert("Erro ao salvar: " + (data.mensagem || "Erro desconhecido"));
            }
        } catch (err) {
            alert("Erro de conexão ao salvar: " + err.message);
        }
    }
'''
        html = html[:idx_fim_script] + funcao_salvar + html[idx_fim_script:]
        print("✅ Função JavaScript 'salvarRelatorioConsolidado' adicionada.")
else:
    print("ℹ️ A função 'salvarRelatorioConsolidado' já existe no arquivo.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ Tudo pronto! O botão 'Confirmar e Salvar' foi adicionado ao Relatório Consolidado.")
