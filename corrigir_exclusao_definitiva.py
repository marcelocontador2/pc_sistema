import re, shutil, datetime, os

arquivos = [
    (r"pc_frontend\analise_comparativo_receitas.html", "/excluir_multiplos_comparativo_receitas"),
    (r"pc_frontend\analise_comparativo_despesas.html", "/excluir_multiplos_comparativo_despesas")
]

for arq, rota in arquivos:
    if not os.path.exists(arq):
        print(f"[AVISO] Arquivo não encontrado: {arq}")
        continue
    
    shutil.copy2(arq, f"{arq}.bak_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    with open(arq, "r", encoding="utf-8") as f:
        html = f.read()
    
    # 1. Substituir a função de exclusão (qualquer versão) pela nova versão múltipla
    # Vamos buscar "function excluirSelecionado()" até o fechamento da função (primeiro "}" no mesmo nível)
    padrao_func = re.compile(r'function excluirSelecionado\(\)\s*\{[^}]*?\n\s*\}', re.DOTALL)
    
    nova_func = f"""function excluirSelecionado() {{
            const checks = document.querySelectorAll('.check-historico:checked, input[name="historico"]:checked');
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
        print(f"[OK] Função de exclusão múltipla aplicada em {os.path.basename(arq)}.")
    else:
        print(f"[AVISO] Função de exclusão não encontrada em {os.path.basename(arq)}.")
    
    # 2. Garantir que os checkboxes gerados tenham a class correta
    # O código original gera `<input type="checkbox" name="historico" value="${item.id}">` ou similar
    # Vamos adicionar a class="check-historico" em todos
    html = re.sub(r'<input[^>]*type="checkbox"[^>]*>', 
                  lambda m: m.group(0).replace('<input', '<input class="check-historico"') if 'class=' not in m.group(0) else m.group(0),
                  html)
    
    with open(arq, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] Checkboxes de {os.path.basename(arq)} padronizados.")

# 3. Backend: garante as rotas
arq_main = r"pc_backend\main.py"
with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

rotas_faltando = []
if "/excluir_multiplos_comparativo_receitas" not in main_code:
    rotas_faltando.append(('receitas', 'historico_comparativo_receitas'))
if "/excluir_multiplos_comparativo_despesas" not in main_code:
    rotas_faltando.append(('despesas', 'historico_comparativo_despesas'))

for nome, tabela in rotas_faltando:
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
    print(f"[OK] Rota {nome} criada no backend.")

if rotas_faltando:
    with open(arq_main, "w", encoding="utf-8") as f:
        f.write(main_code)
else:
    print("[INFO] Rotas de backend já existem.")

print("\n=== PROXIMO PASSO ===")
print("1. REINICIE o servidor uvicorn.")
print("2. Nas telas de comparativo, aperte Ctrl+Shift+R.")
print("3. Marque vários itens e clique em Excluir.")
