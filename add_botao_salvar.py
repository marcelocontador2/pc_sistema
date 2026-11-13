import shutil
import re

caminho = "pc_frontend/integridade.html"
shutil.copy(caminho, caminho + ".bak_add_salvar")

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Adicionar o botão HTML "Confirmar e Salvar" (logo após o botão Gerar PDF)
if 'id="btn-salvar"' not in html:
    # Procura o botão Gerar PDF
    idx_btn = html.find('Gerar PDF</button>')
    if idx_btn != -1:
        # Encontra o fechamento da tag <button> do Gerar PDF
        fim_btn = html.find('>', idx_btn) + 1
        botao_novo = '\n            <button id="btn-salvar" class="btn btn-success" onclick="salvarMatriz()" style="margin-left: 10px; background-color: #198754; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; font-weight: bold;">Confirmar e Salvar</button>'
        html = html[:fim_btn] + botao_novo + html[fim_btn:]
        print("✅ Botão HTML adicionado.")

# 2. Adicionar a função salvarMatriz() se ela não existir
if "function salvarMatriz(" not in html:
    idx_script = html.find("function salvarJustificativa()")
    if idx_script != -1:
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
        html = html[:idx_script] + funcao_salvar + html[idx_script:]
        print("✅ Função JavaScript salvarMatriz() adicionada.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Tudo pronto! O botão 'Confirmar e Salvar' foi adicionado.")
