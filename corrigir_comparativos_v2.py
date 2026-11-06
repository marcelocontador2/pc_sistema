import re, shutil, datetime, os

arquivos = [
    (r"pc_frontend\analise_comparativo_receitas.html", "/excluir_multiplos_comparativo_receitas", "receitas"),
    (r"pc_frontend\analise_comparativo_despesas.html", "/excluir_multiplos_comparativo_despesas", "despesas")
]

for arq, rota, nome_modulo in arquivos:
    if not os.path.exists(arq):
        print(f"[AVISO] Arquivo não encontrado: {arq}")
        continue
    
    shutil.copy2(arq, f"{arq}.bak_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
    print(f"\n[OK] Processando: {os.path.basename(arq)}")
    
    with open(arq, "r", encoding="utf-8") as f:
        html = f.read()
    
    # 1. SUBSTITUIR A FUNÇÃO carregarHistorico INTEIRA
    # Ela é quem monta a lista e os checkboxes. Vamos garantir que use class="check-historico"
    padrao_hist = re.compile(r'function carregarHistorico\(\)\s*\{.*?\n\s*\}', re.DOTALL)
    
    nova_hist = """function carregarHistorico() {
            fetch('/historico_comparativo_""" + nome_modulo + """')
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
                                    <span style="font-size: 14px; font-weight: bold;">${item.periodo}</span>
                                    <span style="font-size: 11px; color: #888;">(${item.data_geracao})</span>
                                </label>
                            </li>`;
                        });
                    }
                    document.getElementById('lista-historico').innerHTML = html;
                })
                .catch(e => console.error("Erro ao carregar histórico:", e));
        }"""
    
    if padrao_hist.search(html):
        html = padrao_hist.sub(nova_hist, html, count=1)
        print(f"  [OK] Função carregarHistorico substituída para o módulo {nome_modulo}.")
    else:
        print(f"  [AVISO] Função carregarHistorico não encontrada em {os.path.basename(arq)}.")
    
    # 2. SUBSTITUIR A FUNÇÃO excluirSelecionado INTEIRA
    padrao_func = re.compile(r'function excluirSelecionado\(\)\s*\{.*?\n\s*\}', re.DOTALL)
    
    nova_func = """function excluirSelecionado() {
            const checks = document.querySelectorAll('.check-historico:checked');
            if (checks.length === 0) { alert("Selecione pelo menos um item no histórico."); return; }
            if (!confirm(`Excluir ${checks.length} item(ns) do histórico?`)) return;
            
            const ids = Array.from(checks).map(c => parseInt(c.value));
            
            fetch("/excluir_multiplos_comparativo_""" + nome_modulo + """", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ids: ids })
            })
            .then(r => r.json())
            .then(data => {
                if (data.ok) {
                    carregarHistorico();
                } else {
                    alert("Erro ao excluir: " + (data.mensagem || "Falha no servidor"));
                }
            })
            .catch(e => alert("Erro de conexão ao excluir."));
        }"""
    
    if padrao_func.search(html):
        html = padrao_func.sub(nova_func, html, count=1)
        print(f"  [OK] Função excluirSelecionado substituída para o módulo {nome_modulo}.")
    else:
        print(f"  [AVISO] Função excluirSelecionado não encontrada em {os.path.basename(arq)}.")
    
    # 3. Garantir que o ID da div do histórico seja sempre "lista-historico"
    html = re.sub(r'id="historico-lista"', 'id="lista-historico"', html)
    html = re.sub(r'id="historico_lista"', 'id="lista-historico"', html)
    
    with open(arq, "w", encoding="utf-8") as f:
        f.write(html)

# 4. Backend: garantir as rotas
arq_main = r"pc_backend\main.py"
with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

rotas_novas = []
for nome, tabela in [("receitas", "historico_comparativo_receitas"), ("despesas", "historico_comparativo_despesas")]:
    if f"/excluir_multiplos_comparativo_{nome}" not in main_code:
        rota = f'''
@app.post("/excluir_multiplos_comparativo_{nome}")
async def excluir_multiplos_comparativo_{nome}(request: Request):
    import sqlite3, os
    try:
        dados = await request.json()
        ids = [int(i) for i in dados.get("ids", []) if str(i).isdigit()]
        if not ids:
            return {{"erro": True, "mensagem": "Nenhum ID válido"}}
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        placeholders = ','.join('?' for _ in ids)
        cursor.execute(f"DELETE FROM {tabela} WHERE id IN ({{placeholders}})", ids)
        conn.commit()
        conn.close()
        return {{"ok": True, "mensagem": f"{{cursor.rowcount}} itens excluídos"}}
    except Exception as e:
        return {{"erro": True, "mensagem": str(e)}}
'''
        main_code += "\n" + rota
        rotas_novas.append(nome)

if rotas_novas:
    with open(arq_main, "w", encoding="utf-8") as f:
        f.write(main_code)
    print(f"\n[OK] Rotas de backend adicionadas: {rotas_novas}")
else:
    print("\n[INFO] Rotas de backend já existem.")

print("\n=== PROXIMO PASSO ===")
print("1. REINICIE o servidor uvicorn.")
print("2. Nas telas de comparativo, aperte Ctrl+Shift+R.")
print("3. Marque vários itens e clique em Excluir.")
