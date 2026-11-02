c = open('main.py', encoding='utf-8-sig').read()

if 'def salvar_relatorio_v2' not in c:
    nova_rota = r'''
@app.post("/salvar_relatorio_v2")
async def salvar_relatorio_v2(request: Request):
    import sqlite3, os, json
    from datetime import datetime
    dados = await request.json()
    periodo = dados.get("periodo")
    texto_total = dados.get("texto_total")
    texto_concentracao = dados.get("texto_concentracao")
    texto_alertas = dados.get("texto_alertas")
    texto_recomendacoes = dados.get("texto_recomendacoes")
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS relatorio_v2_salvo (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, texto_total TEXT,
        texto_concentracao TEXT, texto_alertas TEXT, texto_recomendacoes TEXT, data_edicao TEXT)""")
    
    data_edicao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cur.execute("""INSERT INTO relatorio_v2_salvo 
        (periodo, texto_total, texto_concentracao, texto_alertas, texto_recomendacoes, data_edicao)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (periodo, texto_total, texto_concentracao, texto_alertas, texto_recomendacoes, data_edicao))
    conn.commit()
    conn.close()
    return {"ok": True, "id": cur.lastrowid}
'''
    if 'if __name__ == "__main__":' in c:
        c = c.replace('if __name__ == "__main__":', nova_rota + '\nif __name__ == "__main__":')
    else:
        c += "\n" + nova_rota
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] Rota /salvar_relatorio_v2 criada!")
else:
    print("[AVISO] Rota já existe.")
