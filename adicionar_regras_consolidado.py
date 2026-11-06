import re, shutil, datetime

# =========================================================
# 1. FRONTEND: Adicionar Checkbox, Exibir e Excluir no relatorio_consolidado.html
# =========================================================
arq_html = r"pc_frontend\relatorio_consolidado.html"
shutil.copy2(arq_html, f"{arq_html}.bak_checkbox_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")

with open(arq_html, "r", encoding="utf-8") as f:
    html = f.read()

# 1.1 Substituir a função carregarHistorico para incluir checkbox
old_hist = re.search(r'function carregarHistorico\(\)\s*\{.*?\n\s*\}', html, re.DOTALL)
if old_hist:
    new_hist = """function carregarHistorico() {
            fetch('/historico_relatorio_consolidado')
                .then(r => r.json())
                .then(data => {
                    let html = '';
                    if (!data || data.length === 0) {
                        html = '<li>Nenhum histórico.</li>';
                    } else {
                        data.forEach(item => {
                            html += `<li style="margin-bottom: 8px; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                                <label style="display:flex; align-items:center; gap:10px; cursor:pointer;">
                                    <input type="checkbox" class="check-historico" value="${item.id}">
                                    <div>
                                        <div style="font-weight: bold; font-size: 13px;">Período: ${item.periodo}</div>
                                        <div style="font-size: 11px; color: #888;">Gerado em: ${item.data_geracao}</div>
                                    </div>
                                </label>
                            </li>`;
                        });
                    }
                    document.getElementById('lista-historico').innerHTML = html;
                })
                .catch(e => console.error("Erro no histórico:", e));
        }"""
    html = html[:old_hist.start()] + new_hist + html[old_hist.end():]
    print("[OK] Função carregarHistorico atualizada com checkboxes.")

# 1.2 Adicionar as funções exibirSelecionado e excluirSelecionado
# Vamos injetar antes do "document.addEventListener"
script_extra = """
        async function exibirSelecionado() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert("Selecione um item no histórico."); return; }
            
            try {
                const res = await fetch(`/historico_relatorio_consolidado/${check.value}`);
                const data = await res.json();
                
                if (data.erro) { alert("Erro ao carregar histórico."); return; }
                
                // Se o backend retornar os dados, preenche a tela de status
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
                
            } catch(e) {
                alert("Erro de conexão ao exibir histórico.");
            }
        }

        async function excluirSelecionado() {
            const checks = document.querySelectorAll('.check-historico:checked');
            if (checks.length === 0) { alert("Selecione pelo menos um item no histórico."); return; }
            if (!confirm(`Excluir ${checks.length} item(ns) do histórico?`)) return;
            
            const ids = Array.from(checks).map(c => parseInt(c.value));
            
            try {
                const res = await fetch("/excluir_multiplos_relatorio_consolidado", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ ids: ids })
                });
                const data = await res.json();
                if (data.ok) {
                    carregarHistorico();
                } else {
                    alert("Erro ao excluir: " + (data.mensagem || "Falha no servidor"));
                }
            } catch(e) {
                alert("Erro de conexão ao excluir.");
            }
        }
"""
idx_add = html.find("document.addEventListener('DOMContentLoaded'")
if idx_add != -1:
    html = html[:idx_add] + script_extra + "\n        " + html[idx_add:]

# 1.3 Habilitar os botões Exibir e Excluir no HTML (remover disabled)
html = html.replace('<button id="btn-exibir" class="btn btn-verde" disabled>', '<button id="btn-exibir" class="btn btn-verde">')
html = html.replace('<button id="btn-excluir" class="btn btn-vermelho" disabled>', '<button id="btn-excluir" class="btn btn-vermelho">')

# 1.4 Adicionar o event listener para os botões
html = html.replace(
    "document.getElementById('btn-salvar').addEventListener('click', salvarConsolidado);",
    "document.getElementById('btn-salvar').addEventListener('click', salvarConsolidado);\n            document.getElementById('btn-exibir').addEventListener('click', exibirSelecionado);\n            document.getElementById('btn-excluir').addEventListener('click', excluirSelecionado);"
)

with open(arq_html, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Funções Exibir e Excluir adicionadas e botões habilitados.")

# =========================================================
# 2. BACKEND: Criar rotas de busca por ID e exclusão múltipla
# =========================================================
arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_rotas_hist_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

# Rota GET para pegar os dados do histórico por ID
if "/historico_relatorio_consolidado/{id}" not in main_code:
    rota_get = '''
@app.get("/historico_relatorio_consolidado/{id}")
async def get_historico_consolidado(id: int):
    import sqlite3, json, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"erro": "Histórico não encontrado"}
        
    return {
        "periodo": row[0],
        "data_geracao": row[1],
        "dados": json.loads(row[2])
    }
'''
    main_code += "\n" + rota_get
    print("[OK] Rota GET /historico_relatorio_consolidado/{id} criada.")

# Rota POST para exclusão múltipla
if "/excluir_multiplos_relatorio_consolidado" not in main_code:
    rota_excluir = '''
@app.post("/excluir_multiplos_relatorio_consolidado")
async def excluir_multiplos_relatorio_consolidado(request: Request):
    import sqlite3, os
    try:
        dados = await request.json()
        ids = [int(i) for i in dados.get("ids", []) if str(i).isdigit()]
        if not ids:
            return {"erro": True, "mensagem": "Nenhum ID válido"}
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        placeholders = ','.join('?' for _ in ids)
        cursor.execute(f"DELETE FROM historico_relatorio_consolidado WHERE id IN ({placeholders})", ids)
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": f"{cursor.rowcount} itens excluídos"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
'''
    main_code += "\n" + rota_excluir
    print("[OK] Rota POST /excluir_multiplos_relatorio_consolidado criada.")

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(main_code)

print("\n=== PROXIMO PASSO ===")
print("1. REINICIE o servidor uvicorn.")
print("2. Aperte Ctrl+Shift+R no navegador.")
print("3. Agora a lista lateral deve ter checkboxes e os botões Exibir/Excluir devem funcionar.")
