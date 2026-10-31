c = open('main.py', encoding='utf-8-sig').read()

# Evita duplicar se já existir
if 'def api_configuracoes_custo_pessoal_get' not in c:
    novas_rotas = r'''
@app.get("/api/configuracoes/custo_pessoal")
def api_configuracoes_custo_pessoal_get():
    import sqlite3, os
    from fastapi.responses import JSONResponse
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT valor FROM configuracoes WHERE chave = 'tipo_entidade'")
        row = cur.fetchone()
        conn.close()
        entidade = row[0] if row else "COFEN"
        return {"tipo_entidade": entidade}
    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)

@app.post("/api/configuracoes/custo_pessoal")
async def api_configuracoes_custo_pessoal_post(request: Request):
    import sqlite3, os
    from fastapi.responses import JSONResponse
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    try:
        dados = await request.json()
        entidade = dados.get("tipo_entidade", "COFEN").upper()
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES ('tipo_entidade', ?)", (entidade,))
        conn.commit()
        conn.close()
        return {"ok": True, "tipo_entidade": entidade}
    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)
'''
    if 'if __name__ == "__main__":' in c:
        c = c.replace('if __name__ == "__main__":', novas_rotas + '\nif __name__ == "__main__":')
    else:
        c += "\n" + novas_rotas

open('main.py', 'w', encoding='utf-8').write(c)
print('[OK] Rotas de configuração (GET/POST) criadas!')
