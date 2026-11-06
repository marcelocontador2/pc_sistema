import glob, os, shutil

# 1. Encontra o backup mais recente (antes da última alteração)
backups = glob.glob(r"pc_frontend\relatorio_consolidado.html.bak_*")

if not backups:
    print("[ERRO] Nenhum backup encontrado.")
    exit()

backup_mais_recente = max(backups, key=os.path.getctime)
print(f"Restaurando do backup: {backup_mais_recente}")
shutil.copy2(backup_mais_recente, r"pc_frontend\relatorio_consolidado.html")
print("[OK] Arquivo restaurado. Os botões devem voltar a funcionar (mas sem o checkbox).")

# 2. Vamos fazer as alterações cirúrgicas de forma segura
arq = r"pc_frontend\relatorio_consolidado.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# Adiciona o CSS do checkbox no cabeçalho
if ".check-historico" not in html:
    html = html.replace("</style>", """
        .check-historico { width: 16px; height: 16px; cursor: pointer; }
    </style>""")

# Altera a renderização da lista de histórico para incluir checkbox
# Procura a linha exata que renderiza o <li>
html = html.replace(
    "html += `<li><b>Período:</b> ${item.periodo}<br><small>Gerado em: ${item.data_geracao}</small></li>`;",
    """html += `<li style="margin-bottom: 8px; padding-bottom: 5px; border-bottom: 1px solid #eee;">
                    <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                        <input type="checkbox" class="check-historico" value="${item.id}">
                        <div>
                            <b>Período:</b> ${item.periodo}<br>
                            <small>Gerado em: ${item.data_geracao}</small>
                        </div>
                    </label>
                </li>`;"""
)

# Adiciona as funções de Exibir e Excluir antes do DOMContentLoaded
novas_funcoes = """
        async function exibirSelecionado() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert("Selecione um item no histórico."); return; }
            try {
                const res = await fetch(`/historico_relatorio_consolidado/${check.value}`);
                const data = await res.json();
                if (data.erro) { alert("Erro ao carregar histórico."); return; }
                
                const statusArea = document.getElementById('status-area');
                const modulosArea = document.getElementById('modulos-area');
                
                statusArea.innerHTML = `<div class="status-box status-ok">
                    <strong>✓ Histórico carregado!</strong>
                    <p>Período ${data.periodo} (salvo em ${data.data_geracao})</p>
                </div>`;
                
                let html = '<h3>Módulos Consolidados:</h3>';
                const dados = data.dados || data;
                if (dados.dados) {
                    for (const chave in dados.dados) {
                        const m = dados.dados[chave];
                        html += `<div class="modulo-item">
                            <span>${m.nome}</span>
                            <span class="modulo-ok">✓ ${m.data_geracao}</span>
                        </div>`;
                    }
                }
                modulosArea.innerHTML = html;
            } catch(e) { alert("Erro de conexão."); }
        }

        async function excluirSelecionado() {
            const checks = document.querySelectorAll('.check-historico:checked');
            if (checks.length === 0) { alert("Selecione pelo menos um item."); return; }
            if (!confirm(`Excluir ${checks.length} item(ns)?`)) return;
            const ids = Array.from(checks).map(c => parseInt(c.value));
            try {
                const res = await fetch("/excluir_multiplos_relatorio_consolidado", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ ids: ids })
                });
                const data = await res.json();
                if (data.ok) { carregarHistorico(); } else { alert("Erro: " + (data.mensagem || "Falha")); }
            } catch(e) { alert("Erro de conexão."); }
        }
"""
html = html.replace("document.addEventListener('DOMContentLoaded'", novas_funcoes + "\n        document.addEventListener('DOMContentLoaded'")

# Remove o disabled dos botões Exibir e Excluir (se existirem)
html = html.replace('<button id="btn-exibir" class="btn btn-verde" disabled>', '<button id="btn-exibir" class="btn btn-verde">')
html = html.replace('<button id="btn-excluir" class="btn btn-vermelho" disabled>', '<button id="btn-excluir" class="btn btn-vermelho">')

# Adiciona os event listeners no DOMContentLoaded
html = html.replace(
    "document.getElementById('btn-salvar').addEventListener('click', salvarConsolidado);",
    """document.getElementById('btn-salvar').addEventListener('click', salvarConsolidado);
            document.getElementById('btn-exibir').addEventListener('click', exibirSelecionado);
            document.getElementById('btn-excluir').addEventListener('click', excluirSelecionado);"""
)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Alterações cirúrgicas aplicadas com sucesso.")
print("\n=== PROXIMO PASSO ===")
print("1. Não precisa reiniciar o servidor (só mudou HTML).")
print("2. Aperte Ctrl+Shift+R no navegador.")
print("3. Teste os botões Exibir e Excluir com os checkboxes.")
