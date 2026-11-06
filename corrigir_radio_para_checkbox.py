import re, shutil, datetime, os

arquivos = [
    (r"pc_frontend\analise_comparativo_receitas.html", "/excluir_multiplos_comparativo_receitas", "receitas"),
    (r"pc_frontend\analise_comparativo_despesas.html", "/excluir_multiplos_comparativo_despesas", "despesas")
]

for arq, rota, nome_modulo in arquivos:
    if not os.path.exists(arq):
        continue
    
    shutil.copy2(arq, f"{arq}.bak_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
    print(f"\n[OK] Processando: {os.path.basename(arq)}")
    
    with open(arq, "r", encoding="utf-8") as f:
        html = f.read()
    
    # 1. Trocar radio por checkbox na renderização do histórico
    html = re.sub(
        r'<input type="radio" name="historico" value="\$\{item\.id\}">',
        r'<input type="checkbox" class="check-historico" value="${item.id}">',
        html
    )
    print("  [OK] Checkboxes 'radio' substituídos por 'checkbox'.")
    
    # 2. Substituir a função excluirSelecionado (qualquer variação)
    padrao_func = re.compile(r'(async\s+)?function excluirSelecionado\(\)\s*\{.*?\n\s*\}', re.DOTALL)
    
    nova_func = f"""function excluirSelecionado() {{
            const checks = document.querySelectorAll('.check-historico:checked');
            if (checks.length === 0) {{ alert("Selecione pelo menos um item no histórico."); return; }}
            if (!confirm(`Excluir ${{checks.length}} item(ns) do histórico?`)) return;
            
            const ids = Array.from(checks).map(c => parseInt(c.value));
            
            fetch("{rota}", {{
                method: "POST",
                headers: {{ "Content-Type": "application/json" }},
                body: JSON.stringify({{ ids: ids }})
            }})
            .then(r => r.json())
            .then(data => {{
                if (data.ok) {{
                    carregarHistorico();
                }} else {{
                    alert("Erro ao excluir: " + (data.mensagem || "Falha no servidor"));
                }}
            }})
            .catch(e => alert("Erro de conexão ao excluir."));
        }}"""
    
    if padrao_func.search(html):
        html = padrao_func.sub(nova_func, html, count=1)
        print("  [OK] Função de exclusão múltipla aplicada.")
    else:
        print("  [AVISO] Função de exclusão não encontrada.")
    
    with open(arq, "w", encoding="utf-8") as f:
        f.write(html)

# 3. Backend: garantir rotas
arq_main = r"pc_backend\main.py"
with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

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
        print(f"[OK] Rota de exclusão múltipla de {nome} criada no backend.")

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(main_code)

print("\n=== PROXIMO PASSO ===")
print("1. REINICIE o servidor uvicorn.")
print("2. Nas telas de comparativo, aperte Ctrl+Shift+R.")
print("3. Marque vários itens e clique em Excluir.")
