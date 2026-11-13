import re
import shutil

caminho = "pc_frontend/integridade.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_auditoria_postgres")

# Encontra a função verificarEGerar
idx_inicio = html.find("async function verificarEGerar(")
if idx_inicio == -1:
    idx_inicio = html.find("function verificarEGerar(")

if idx_inicio != -1:
    i = html.find("{", idx_inicio)
    contador = 1
    i += 1
    while i < len(html) and contador > 0:
        if html[i] == "{": contador += 1
        elif html[i] == "}": contador -= 1
        i += 1
    
    # Nova função focada em salvar no Postgres e recarregar o histórico correto
    nova_verificar = '''async function verificarEGerar() {
        const ano = document.getElementById('ano').value;
        const tipo = document.getElementById('tipo_periodo').value;
        const trimestre = document.getElementById('trimestre').value;
        const periodo = `${ano}-${tipo}-${trimestre}`;

        const container = document.getElementById('integridade-cards');
        if (container) container.innerHTML = '<div class="loading" style="padding: 20px; color: #004b8d; font-weight: bold;">Gerando e salvando no PostgreSQL...</div>';

        try {
            // 1. Força o backend a recalcular e salvar no Postgres
            const resSalvar = await fetch(`/api/integridade_matriz/${periodo}/salvar`, { method: 'POST' });
            
            if (!resSalvar.ok) {
                // Se a rota de salvar falhar, avisa na tela (pode ser erro no Postgres)
                const erroTxt = await resSalvar.text();
                throw new Error(`A rota de salvar retornou erro ${resSalvar.status}. Detalhes: ${erroTxt.substring(0, 100)}`);
            }
            
            const dataSalvar = await resSalvar.json();
            if (dataSalvar.erro) {
                throw new Error("Backend recusou a geração: " + dataSalvar.mensagem);
            }

            if (container) container.innerHTML = '<div class="loading" style="padding: 20px;">Matriz salva! Buscando dados do histórico...</div>';

            // 2. Recarrega a lista lateral
            await carregarHistorico();

            // 3. Pega o primeiro item da lista (o mais recente que acabou de ser salvo)
            const list = document.getElementById('lista-historico');
            if (list && list.children.length > 0) {
                // Desmarca todos, marca o primeiro e clica nele
                list.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
                const primeiroCheckbox = list.querySelector('input[type="checkbox"]');
                
                if (primeiroCheckbox) {
                    primeiroCheckbox.checked = true;
                    // A função exibirSelecionado() vai buscar do banco e renderizar o layout azul perfeito
                    await exibirSelecionado(); 
                }
            } else {
                if (container) container.innerHTML = '<div style="color: orange; padding: 20px;">Matriz salva, mas nenhum histórico foi encontrado na lista.</div>';
            }

        } catch (err) {
            console.error("Erro na geração da matriz:", err);
            if (container) container.innerHTML = `<div style="color: red; padding: 20px; background: #ffe6e6; border: 1px solid red;">
                <strong>Falha ao gerar matriz no PostgreSQL.</strong><br>
                Isso indica que a rota POST <code>/api/integridade_matriz/${periodo}/salvar</code> está falhando.<br>
                Verifique o terminal do Python para ver o erro do banco de dados.<br>
                <small>Erro técnico: ${err.message}</small>
            </div>`;
        }
    }'''

    html = html[:idx_inicio] + nova_verificar + html[i:]

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Função 'verificarEGerar' ajustada para o fluxo do PostgreSQL!")
else:
    print("❌ Função 'verificarEGerar' não encontrada no arquivo.")
