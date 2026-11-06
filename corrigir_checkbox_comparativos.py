import re, shutil, datetime, os

# =========================================================
# 1. FRONTEND: CORRIGIR OS CHECKBOXES E A EXCLUSÃO
# =========================================================
arquivos = [
    r"pc_frontend\analise_comparativo_receitas.html",
    r"pc_frontend\analise_comparativo_despesas.html"
]

for arq in arquivos:
    if not os.path.exists(arq):
        print(f"[AVISO] Arquivo não encontrado: {arq}")
        continue
        
    shutil.copy2(arq, f"{arq}.bak_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
    print(f"\n[OK] Analisando: {arq}")
    
    with open(arq, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Corrigir o HTML dos checkboxes gerados pelo JS
    # Procura onde ele injeta o checkbox no HTML (geralmente no loop de itens)
    # Vamos garantir que ele tenha type="checkbox", class="check-historico" e name="historico_item"
    # E garantir que o value seja o ID.
    
    # Se o HTML estiver usando algo como: <input type="checkbox" ... >, vamos garantir que ele não use IDs fixos
    # (IDs fixos impedem marcar mais de um)
    
    # Substitui o seletor do botão de exclusão e a função
    padrao_btn = re.compile(r'<button[^>]*onclick="excluirSelecionado\(\)"[^>]*>.*?</button>', re.DOTALL | re.IGNORECASE)
    if padrao_btn.search(html):
        html = padrao_btn.sub('<button class="btn btn-excluir" onclick="excluirSelecionado()">Excluir Selecionado</button>', html, count=1)
    
    # Substitui a função de exclusão para múltiplos
    padrao_func = re.compile(r'async function excluirSelecionado\(\)\s*\{.*?\n\s*\}', re.DOTALL)
    
    # Define a nova função de exclusão (igual à do panorama)
    if "receitas" in arq:
        rota = "/excluir_multiplos_comparativo_receitas"
    else:
        rota = "/excluir_multiplos_comparativo_despesas"
        
    nova_func = f"""async function excluirSelecionado() {{
            const checks = document.querySelectorAll('.check-historico:checked');
            if (checks.length === 0) {{ alert("Selecione pelo menos um item no histórico."); return; }}
            if (!confirm(`Excluir ${{checks.length}} item(ns) do histórico?`)) return;
            
            const ids = Array.from(checks).map(c => parseInt(c.value));
            
            try {{
                const res = await fetch("{rota}", {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/json" }},
                    body: JSON.stringify({{ ids: ids }})
                }});
                const data = await res.json();
                if (data.ok) {{
                    carregarHistorico();
                }} else {{
                    alert("Erro ao excluir: " + (data.mensagem || "Falha no servidor"));
                }}
            }} catch(e) {{
                alert("Erro de conexão ao excluir.");
            }}
        }}"""
        
    if padrao_func.search(html):
        html = padrao_func.sub(nova_func, html, count=1)
        print("  [OK] Função de exclusão múltipla substituída.")
    else:
        print("  [AVISO] Função de exclusão antiga não encontrada.")
        
    # 2. Corrigir o HTML do checkbox na renderização
    # Vamos buscar a linha onde o checkbox é criado (geralmente tem type="checkbox")
    # Se ele estiver usando id="check-historico" em vez de class, isso trava a marcação múltipla.
    # Vamos garantir que seja class e que o value seja único.
    
    # O padrão comum é: <input type="checkbox" class="check-historico" value="${item.id}">
    # Vamos substituir qualquer id fixo por class.
    html = re.sub(r'<input[^>]*type="checkbox"[^>]*id="[^"]*"[^>]*>', 
                  r'<input type="checkbox" class="check-historico" value="${item.id}">', 
                  html)
    
    # Caso o JS monte o HTML do checkbox dentro de template string, vamos verificar se está correto.
    # Substitui a forma de renderização do checkbox se necessário.
    html = re.sub(r'<input[^>]*type="checkbox"[^>]*>', 
                  r'<input type="checkbox" class="check-historico" value="${item.id}">', 
                  html)
    
    with open(arq, "w", encoding="utf-8") as f:
        f.write(html)
    print("  [OK] Checkboxes corrigidos para permitir múltipla seleção.")

# =========================================================
# 2. BACKEND: GARANTIR ROTAS (se não existirem)
# =========================================================
arq_main = r"pc_backend\main.py"
with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

if "/excluir_multiplos_comparativo_receitas" not in main_code:
    rota_rec = '''
@app.post("/excluir_multiplos_comparativo_receitas")
async def excluir_multiplos_comparativo_receitas(request: Request):
    import sqlite3, os
    try:
        dados = await request.json()
        ids = [int(i) for i in dados.get("ids", []) if str(i).isdigit()]
        if not ids: return {"erro": True, "mensagem": "Nenhum ID válido"}
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        placeholders = ','.join('?' for _ in ids)
        cursor.execute(f"DELETE FROM historico_comparativo_receitas WHERE id IN ({placeholders})", ids)
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": f"{cursor.rowcount} itens excluídos"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
'''
    main_code += "\n" + rota_rec
    print("[OK] Rota de exclusão múltipla de Receitas adicionada.")

if "/excluir_multiplos_comparativo_despesas" not in main_code:
    rota_desp = '''
@app.post("/excluir_multiplos_comparativo_despesas")
async def excluir_multiplos_comparativo_despesas(request: Request):
    import sqlite3, os
    try:
        dados = await request.json()
        ids = [int(i) for i in dados.get("ids", []) if str(i).isdigit()]
        if not ids: return {"erro": True, "mensagem": "Nenhum ID válido"}
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        placeholders = ','.join('?' for _ in ids)
        cursor.execute(f"DELETE FROM historico_comparativo_despesas WHERE id IN ({placeholders})", ids)
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": f"{cursor.rowcount} itens excluídos"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
'''
    main_code += "\n" + rota_desp
    print("[OK] Rota de exclusão múltipla de Despesas adicionada.")

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(main_code)

print("\n=== PROXIMO PASSO ===")
print("1. REINICIE o servidor uvicorn.")
print("2. Va nas telas de comparativo e aperte Ctrl+Shift+R.")
print("3. Marque varios itens e clique em Excluir.")
