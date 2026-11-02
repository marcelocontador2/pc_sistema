c = open('main.py', encoding='utf-8-sig').read()

if "def serve_analise_centro_custos" not in c:
    novas_rotas = r'''
@app.get("/analise_centro_custos", response_class=HTMLResponse)
def serve_analise_centro_custos():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_centro_custos.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Tela não encontrada</h1>", status_code=404)

@app.get("/api/centro_custos/{periodo}")
def api_centro_custos(periodo: str):
    # Simulação de retorno para testar a integridade dos botões
    return {
        "erro": False,
        "periodo": periodo,
        "centros": [
            {"nome": "Administração", "valor": 150000.00},
            {"nome": "Enfermagem", "valor": 300000.00},
            {"nome": "Tecnologia da Informação", "valor": 200000.00},
            {"nome": "Recursos Humanos", "valor": 100000.00}
        ]
    }

@app.get("/historico_centro_custos")
def get_historico_centro_custos():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_centro_custos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")
    conn.commit()
    cur.execute("SELECT id, periodo, data_geracao FROM historico_centro_custos ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@app.get("/historico_centro_custos/{id}")
def get_historico_centro_custos_id(id: int):
    import sqlite3, os, json
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT periodo, dados_json FROM historico_centro_custos WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"ok": True, "periodo": row[0], "dados": json.loads(row[1])}
    return {"ok": False}

@app.post("/salvar_centro_custos")
async def salvar_centro_custos(request: Request):
    import sqlite3, os, json
    from datetime import datetime
    dados = await request.json()
    periodo = dados.get("periodo", "2026-TRIMESTRE-3")
    dados_json = json.dumps(dados.get("dados", {}))
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("INSERT INTO historico_centro_custos (periodo, data_geracao, dados_json) VALUES (?, ?, ?)", (periodo, data_geracao, dados_json))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/historico_centro_custos/{id}")
def excluir_historico_centro_custos(id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_centro_custos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"ok": True}
'''
    if 'if __name__ == "__main__":' in c:
        c = c.replace('if __name__ == "__main__":', novas_rotas + '\nif __name__ == "__main__":')
    else:
        c += "\n" + novas_rotas
    
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] Rotas do Centro de Custos adicionadas ao main.py!")
else:
    print("[AVISO] Rotas já existem. Nada foi alterado.")
