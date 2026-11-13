import shutil

caminho = "pc_frontend/integridade.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_fix_dinamico")

# 1. Substitui a função verificarEGerar
idx_v = html.find("async function verificarEGerar(")
if idx_v != -1:
    i = html.find("{", idx_v)
    c = 1
    i += 1
    while i < len(html) and c > 0:
        if html[i] == "{": c += 1
        elif html[i] == "}": c -= 1
        i += 1
    
    nova_v = '''async function verificarEGerar() {
        const ano = document.getElementById('ano').value;
        const tipo = document.getElementById('tipo_periodo').value;
        const trimestre = document.getElementById('trimestre').value;
        const periodo = `${ano}-${tipo}-${trimestre}`;

        const container = document.getElementById('integridade-cards');
        if (container) container.innerHTML = '<div class="loading" style="padding: 20px; color: #004b8d; font-weight: bold;">Gerando nova matriz...</div>';

        try {
            // 1. Busca os dados na API (que agora lê os CSVs e gera a matriz)
            const res = await fetch(`/api/integridade_matriz/${periodo}?_t=${Date.now()}`);
            const data = await res.json();

            if (data.erro) {
                throw new Error(data.mensagem || "Erro desconhecido no backend.");
            }

            // 2. Salva os dados gerados no PostgreSQL via rota /salvar
            if (container) container.innerHTML = '<div class="loading" style="padding: 20px; color: #004b8d; font-weight: bold;">Salvando no PostgreSQL...</div>';
            
            const resSalvar = await fetch(`/api/integridade_matriz/${periodo}/salvar`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ matriz: data.matriz, justificativas: data.justificativas || {} })
            });
            
            const saveResult = await resSalvar.json();
            if (saveResult.erro) {
                console.warn("Aviso ao salvar:", saveResult.mensagem);
            }

            // 3. Renderiza a matriz na tela
            dadosAtuais = data;
            renderizarMatriz(data, container);
            
            // 4. Atualiza a lista lateral de históricos para incluir o novo salvamento
            carregarHistorico();

        } catch (err) {
            console.error(err);
            if (container) container.innerHTML = `<div style="color: red; padding: 20px; background: #ffe6e6; border: 1px solid red;">
                <strong>Erro ao gerar matriz:</strong> ${err.message}
            </div>`;
        }
    }'''
    html = html[:idx_v] + nova_v + html[i:]

# 2. Substitui a função excluirSelecionado
idx_e = html.find("function excluirSelecionado(")
if idx_e != -1:
    i = html.find("{", idx_e)
    c = 1
    i += 1
    while i < len(html) and c > 0:
        if html[i] == "{": c += 1
        elif html[i] == "}": c -= 1
        i += 1
        
    nova_e = '''function excluirSelecionado() {
        const id = getHistoricoSelecionado();
        if (!id) { alert("Selecione um histórico na lista lateral para excluir."); return; }
        if (!confirm("Tem certeza que deseja excluir o histórico selecionado?")) return;

        fetch("/excluir_multiplos_integridade_matriz", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ids: [parseInt(id)] })
        })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                // Limpa a tela e atualiza a lista lateral
                document.getElementById('integridade-cards').innerHTML = '';
                carregarHistorico();
            } else {
                alert("Erro ao excluir: " + (data.mensagem || "Erro desconhecido"));
            }
        })
        .catch(err => alert("Erro de conexão ao excluir: " + err));
    }'''
    html = html[:idx_e] + nova_e + html[i:]

with open(caminho, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ Frontend (integridade.html) atualizado: verificar é dinâmico e exclusão corrigida!")
