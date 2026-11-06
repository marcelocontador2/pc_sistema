import re, shutil, datetime

# =========================================================
# 1. BACKEND: Criar rota de exclusão múltipla
# =========================================================
arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_exc_mult_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

# Verifica se a rota já existe para não duplicar
if "@app.post(\"/excluir_panorama_multiplos\")" not in main_code:
    nova_rota = '''
@app.post("/excluir_panorama_multiplos")
async def excluir_panorama_multiplos(request: Request):
    import sqlite3, os
    try:
        dados = await request.json()
        ids = dados.get("ids", [])
        
        if not ids:
            return {"erro": True, "mensagem": "Nenhum ID enviado"}
            
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Cria a string de placeholders (?,?,?)
        placeholders = ','.join('?' for _ in ids)
        cursor.execute(f"DELETE FROM historico_panorama WHERE id IN ({placeholders})", ids)
        
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": f"{cursor.rowcount} itens excluídos"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
'''
    main_code += "\n" + nova_rota
    with open(arq_main, "w", encoding="utf-8") as f:
        f.write(main_code)
    print("[OK] Rota /excluir_panorama_multiplos criada no backend.")

# =========================================================
# 2. FRONTEND: Alterar função excluirSelecionado
# =========================================================
arq_html = r"pc_frontend\panorama.html"
shutil.copy2(arq_html, f"pc_frontend\\panorama_backup_exc_mult_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

with open(arq_html, "r", encoding="utf-8") as f:
    html = f.read()

# Função antiga de exclusão
old_excluir = """async function excluirSelecionado() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert("Selecione um item no histórico."); return; }
            if (!confirm("Excluir este item do histórico?")) return;
            
            try {
                await fetch(`/excluir_panorama/${check.value}`, { method: 'DELETE' });
                carregarHistorico();
            } catch(e) {
                alert("Erro ao excluir.");
            }
        }"""

# Nova função para múltiplos
nova_excluir = """async function excluirSelecionado() {
            const checks = document.querySelectorAll('.check-historico:checked');
            if (checks.length === 0) { alert("Selecione pelo menos um item no histórico."); return; }
            if (!confirm(`Excluir ${checks.length} item(ns) do histórico?`)) return;
            
            const ids = Array.from(checks).map(c => parseInt(c.value));
            
            try {
                const res = await fetch("/excluir_panorama_multiplos", {
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

if old_excluir in html:
    html = html.replace(old_excluir, nova_excluir)
    with open(arq_html, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Função de exclusão múltipla aplicada no frontend.")
else:
    print("[AVISO] Não encontrei a função de exclusão antiga no HTML. Verifique manualmente.")

print("\n=== AÇÃO OBRIGATÓRIA ===")
print("1. Reinicie o servidor uvicorn (Ctrl+C e suba novamente).")
print("2. Va no navegador e aperte Ctrl+Shift+R.")
print("3. Marque vários checkboxes e clique em Excluir Selecionado.")
