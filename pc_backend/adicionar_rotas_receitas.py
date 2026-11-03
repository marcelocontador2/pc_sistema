c = open('main.py', encoding='utf-8-sig').read()

if 'def api_comparativo_receitas' not in c:
    novas_rotas = r'''
# ========== ROTAS DO COMPARATIVO DE RECEITAS ==========
@app.get("/api/comparativo_receitas/{periodo}")
def api_comparativo_receitas(periodo: str):
    import os, csv, io
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    # Simulação: retorna dados fictícios de receitas (adapte para ler o CSV real, se houver)
    receitas = [
        {"nome": "Receita de Serviços", "valor": 120000000.0},
        {"nome": "Receitas Financeiras", "valor": 25000000.0},
        {"nome": "Outras Receitas", "valor": 12000000.0}
    ]
    return {"erro": False, "periodo": periodo, "receitas": receitas}

@app.get("/historico_comparativo_receitas")
def get_historico_comparativo_receitas():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_comparativo_receitas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")
    conn.commit()
    cur.execute("SELECT id, periodo, data_geracao FROM historico_comparativo_receitas ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@app.get("/historico_comparativo_receitas/{id}")
def get_historico_comparativo_receitas_id(id: int):
    import sqlite3, os, json
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT periodo, dados_json FROM historico_comparativo_receitas WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    if row: return {"ok": True, "periodo": row[0], "dados": json.loads(row[1])}
    return {"ok": False}

@app.post("/salvar_comparativo_receitas")
async def salvar_comparativo_receitas(request: Request):
    import sqlite3, os, json
    from datetime import datetime
    dados = await request.json()
    periodo = dados.get("periodo", "2026-TRIMESTRE-3")
    dados_json = json.dumps(dados.get("dados", {}))
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("INSERT INTO historico_comparativo_receitas (periodo, data_geracao, dados_json) VALUES (?, ?, ?)", (periodo, data_geracao, dados_json))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.post("/excluir_multiplos_comparativo_receitas")
async def excluir_multiplos_comparativo_receitas(request: Request):
    import sqlite3, os
    dados = await request.json()
    ids = dados.get("ids", [])
    if not ids: return {"ok": False, "mensagem": "Nenhum ID."}
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    placeholders = ",".join(["?"] * len(ids))
    cur.execute(f"DELETE FROM historico_comparativo_receitas WHERE id IN ({placeholders})", ids)
    conn.commit()
    excluidos = cur.rowcount
    conn.close()
    return {"ok": True, "excluidos": excluidos}

@app.get("/analise_comparativo_receitas", response_class=HTMLResponse)
def serve_analise_comparativo_receitas():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_comparativo_receitas.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Tela não encontrada</h1>", status_code=404)

@app.get("/relatorio_comparativo_receitas", response_class=HTMLResponse)
def serve_relatorio_comparativo_receitas():
    # Por enquanto, redireciona para o relatório de centro de custos (ou crie um novo HTML)
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_final.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatório não encontrado</h1>", status_code=404)
'''
    if 'if __name__ == "__main__":' in c:
        c = c.replace('if __name__ == "__main__":', novas_rotas + '\nif __name__ == "__main__":')
    else:
        c += "\n" + novas_rotas
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] Rotas do Comparativo de Receitas adicionadas ao main.py!")
else:
    print("[AVISO] Rotas já existem.")
