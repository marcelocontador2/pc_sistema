import re, shutil, datetime, os

# =========================================================
# 1. FRONTEND: RECEITAS
# =========================================================
arq_rec = r"pc_frontend\analise_comparativo_receitas.html"
if os.path.exists(arq_rec):
    shutil.copy2(arq_rec, f"pc_frontend\\analise_comparativo_receitas_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    with open(arq_rec, "r", encoding="utf-8") as f:
        html_rec = f.read()

    # Nova função de exclusão múltipla (Receitas)
    nova_func_rec = """async function excluirSelecionado() {
            const checks = document.querySelectorAll('.check-historico:checked');
            if (checks.length === 0) { alert("Selecione pelo menos um item no histórico."); return; }
            if (!confirm(`Excluir ${checks.length} item(ns) do histórico?`)) return;
            
            const ids = Array.from(checks).map(c => parseInt(c.value));
            
            try {
                const res = await fetch("/excluir_multiplos_comparativo_receitas", {
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
        }"""
    
    padrao_rec = re.compile(r'async function excluirSelecionado\(\)\s*\{.*?\n\s*\}', re.DOTALL)
    if padrao_rec.search(html_rec):
        html_rec = padrao_rec.sub(nova_func_rec, html_rec, count=1)
        with open(arq_rec, "w", encoding="utf-8") as f:
            f.write(html_rec)
        print("[OK] Função de exclusão múltipla aplicada em Receitas.")
    else:
        print("[AVISO] Função de exclusão não encontrada em Receitas.")

# =========================================================
# 2. FRONTEND: DESPESAS
# =========================================================
arq_desp = r"pc_frontend\analise_comparativo_despesas.html"
if os.path.exists(arq_desp):
    shutil.copy2(arq_desp, f"pc_frontend\\analise_comparativo_despesas_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    with open(arq_desp, "r", encoding="utf-8") as f:
        html_desp = f.read()

    # Nova função de exclusão múltipla (Despesas)
    nova_func_desp = """async function excluirSelecionado() {
            const checks = document.querySelectorAll('.check-historico:checked');
            if (checks.length === 0) { alert("Selecione pelo menos um item no histórico."); return; }
            if (!confirm(`Excluir ${checks.length} item(ns) do histórico?`)) return;
            
            const ids = Array.from(checks).map(c => parseInt(c.value));
            
            try {
                const res = await fetch("/excluir_multiplos_comparativo_despesas", {
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
        }"""

    padrao_desp = re.compile(r'async function excluirSelecionado\(\)\s*\{.*?\n\s*\}', re.DOTALL)
    if padrao_desp.search(html_desp):
        html_desp = padrao_desp.sub(nova_func_desp, html_desp, count=1)
        with open(arq_desp, "w", encoding="utf-8") as f:
            f.write(html_desp)
        print("[OK] Função de exclusão múltipla aplicada em Despesas.")
    else:
        print("[AVISO] Função de exclusão não encontrada em Despesas.")

# =========================================================
# 3. BACKEND: ADICIONAR ROTAS SE NÃO EXISTIREM
# =========================================================
arq_main = r"pc_backend\main.py"
with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

rotas_novas = []

if "/excluir_multiplos_comparativo_receitas" not in main_code:
    rotas_novas.append('''
@app.post("/excluir_multiplos_comparativo_receitas")
async def excluir_multiplos_comparativo_receitas(request: Request):
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
        cursor.execute(f"DELETE FROM historico_comparativo_receitas WHERE id IN ({placeholders})", ids)
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": "Itens excluídos"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
''')

if "/excluir_multiplos_comparativo_despesas" not in main_code:
    rotas_novas.append('''
@app.post("/excluir_multiplos_comparativo_despesas")
async def excluir_multiplos_comparativo_despesas(request: Request):
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
        cursor.execute(f"DELETE FROM historico_comparativo_despesas WHERE id IN ({placeholders})", ids)
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": "Itens excluídos"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
''')

if rotas_novas:
    main_code += "\n" + "\n".join(rotas_novas)
    with open(arq_main, "w", encoding="utf-8") as f:
        f.write(main_code)
    print("[OK] Rotas de exclusão múltipla adicionadas ao backend.")
else:
    print("[INFO] As rotas de exclusão múltipla já existem no backend.")

print("\n=== PROXIMO PASSO ===")
print("1. REINICIE o servidor uvicorn (Ctrl+C e suba de novo).")
print("2. Va no navegador e aperte Ctrl+Shift+R nas telas de comparativo.")
print("3. Teste marcar varios itens e excluir.")
