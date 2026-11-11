p = 'pc_backend/main.py'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

rotas_mcasp = '''@app.get("/api/notas_mcasp")
async def api_get_notas_mcasp():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, codigo, nivel, titulo, texto, ordem FROM notas_mcasp_modelo ORDER BY ordem")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/api/notas_mcasp/salvar")
async def api_salvar_notas_mcasp(request: Request):
    import sqlite3, os
    body = await request.json()
    itens = body.get("itens", [])
    if not itens:
        return {"ok": False, "mensagem": "Nenhum item enviado"}
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        for item in itens:
            cur.execute("UPDATE notas_mcasp_modelo SET texto = ? WHERE id = ?", (item["texto"], item["id"]))
        conn.commit()
        return {"ok": True}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "mensagem": str(e)}
    finally:
        conn.close()

@app.get("/notas_mcasp")
def rota_notas_mcasp():
    from fastapi.responses import FileResponse
    import os
    caminho = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pc_frontend", "notas_mcasp.html")
    return FileResponse(caminho)

'''

anchor = '@app.get("/gerar_pdf_notas/{id}")'
if '/api/notas_mcasp' in s:
    print('AVISO: rotas ja existem')
else:
    s = s.replace(anchor, rotas_mcasp + anchor, 1)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)
    print('OK: rotas do novo modelo MCASP injetadas no main.py')
