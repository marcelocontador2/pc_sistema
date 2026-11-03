import shutil, ast, datetime

shutil.copy2("main.py", f"main.py.bak_hist_{datetime.datetime.now().strftime('%H%M%S')}")
c = open("main.py", encoding="utf-8-sig").read()

# Novas rotas para o histórico de despesas
novas_rotas = '''
@app.post("/api/comparativo_despesas_v2/{periodo_atual}/salvar")
def salvar_comparativo_despesas(periodo_atual: str):
    import sqlite3, os, json
    from datetime import datetime
    
    # Pega os dados atuais
    dados = api_comparativo_despesas_v2(periodo_atual)
    if dados.get("erro"): return {"erro": True, "mensagem": dados.get("mensagem")}
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_comparativo_despesas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")
        
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")
    dados_json = json.dumps(dados)
    
    cur.execute("INSERT INTO historico_comparativo_despesas (periodo, data_geracao, dados_json) VALUES (?, ?, ?)", (periodo_atual, data_geracao, dados_json))
    conn.commit()
    conn.close()
    return {"erro": False, "mensagem": "Salvo com sucesso!"}

@app.delete("/historico_comparativo_despesas/{id}")
def excluir_comparativo_despesas(id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_comparativo_despesas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"erro": False}

'''

if "salvar_comparativo_despesas" not in c:
    # Insere as rotas antes da função de gerar_pdf
    idx = c.find('@app.get("/gerar_pdf_comparativo_despesas")')
    if idx != -1:
        c = c[:idx] + novas_rotas + "\n" + c[idx:]
        open("main.py", "w", encoding="utf-8").write(c)
        print("[OK] Rotas de Salvar e Excluir adicionadas ao Backend!")
        ast.parse(open("main.py", encoding="utf-8").read())
        print("[OK] Sintaxe OK!")
    else:
        print("[ERRO] Ponto de inserção não encontrado.")
else:
    print("[AVISO] Rotas já existem.")
