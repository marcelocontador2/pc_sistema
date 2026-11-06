import re, shutil, datetime

# =========================================================
# 1. BACKEND: Aceitar IDs como string ou int
# =========================================================
arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_fix_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

padrao_rota = re.compile(r'@app\.post\("/excluir_panorama_multiplos"\).*?(?=\n@app\.|\n@app\.get|\Z)', re.DOTALL)

nova_rota = '''@app.post("/excluir_panorama_multiplos")
async def excluir_panorama_multiplos(request: Request):
    import sqlite3, os
    try:
        dados = await request.json()
        ids_brutos = dados.get("ids", [])
        
        if not ids_brutos:
            return {"erro": True, "mensagem": "Nenhum ID enviado"}
            
        # Garante que todos são inteiros (para o SQLite)
        ids = [int(i) for i in ids_brutos if str(i).strip().isdigit()]
        
        if not ids:
            return {"erro": True, "mensagem": "IDs inválidos"}
            
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        placeholders = ','.join('?' for _ in ids)
        cursor.execute(f"DELETE FROM historico_panorama WHERE id IN ({placeholders})", ids)
        excluidos = cursor.rowcount
        conn.commit()
        conn.close()
        
        return {"ok": True, "mensagem": f"{excluidos} itens excluídos"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
'''

main_code = padrao_rota.sub(nova_rota, main_code)

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(main_code)
print("[OK] Backend reforçado (aceita IDs como string ou int).")

# =========================================================
# 2. FRONTEND: Função robusta com logs de erro
# =========================================================
arq_html = r"pc_frontend\panorama.html"
shutil.copy2(arq_html, f"pc_frontend\\panorama_backup_fix_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

with open(arq_html, "r", encoding="utf-8") as f:
    html = f.read()

# Substitui o bloco da função de exclusão antiga pela nova com log
padrao_func = re.compile(r'async function excluirSelecionado\(\)\s*\{.*?\n        \}', re.DOTALL)

nova_func = '''async function excluirSelecionado() {
            const checks = document.querySelectorAll('.check-historico:checked');
            if (checks.length === 0) { alert("Selecione pelo menos um item no histórico."); return; }
            if (!confirm(`Excluir ${checks.length} item(ns) do histórico?`)) return;
            
            const ids = Array.from(checks).map(c => parseInt(c.value));
            console.log("IDs para excluir:", ids);
            
            try {
                const res = await fetch("/excluir_panorama_multiplos", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ ids: ids })
                });
                
                console.log("Status da resposta:", res.status);
                const data = await res.json();
                console.log("Resposta do servidor:", data);
                
                if (data.ok) {
                    carregarHistorico();
                } else {
                    alert("Erro ao excluir: " + (data.mensagem || "Falha no servidor"));
                }
            } catch(e) {
                console.error("Erro de conexão:", e);
                alert("Erro de conexão ao excluir. Verifique o Console (F12).");
            }
        }'''

if padrao_func.search(html):
    html = padrao_func.sub(nova_func, html)
    with open(arq_html, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Frontend reforçado com logs de erro no console.")
else:
    print("[AVISO] Não encontrei a função de exclusão no frontend.")

print("\n=== AÇÃO OBRIGATÓRIA ===")
print("1. REINICIE O SERVIDOR (Ctrl+C e suba novamente).")
print("2. No navegador: Ctrl+Shift+R.")
print("3. Aperte F12 e vá na aba Console para ver os logs.")
print("4. Marque vários itens e clique em Excluir Selecionado.")
