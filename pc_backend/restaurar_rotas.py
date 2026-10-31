import re

c = open('main.py', encoding='utf-8-sig').read()

# 1. Remover a função vazia
c = re.sub(r'@app\.get\("/analise_custo_pessoal", response_class=HTMLResponse\)\s*\n\s*def serve_analise_custo_pessoal\(\):\s*\n\s*\n', '', c)

# 2. Inserir a rota funcional no lugar (antes do if __name__)
rota_analise = r'''
@app.get("/analise_custo_pessoal", response_class=HTMLResponse)
def serve_analise_custo_pessoal():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_custo_pessoal.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
    return HTMLResponse(content="<h1>Arquivo analise_custo_pessoal.html não encontrado!</h1>", status_code=404)
'''

if 'if __name__ == "__main__":' in c:
    c = c.replace('if __name__ == "__main__":', rota_analise + '\nif __name__ == "__main__":')
else:
    c += "\n" + rota_analise

# 3. Garantir que a rota do histórico existe (se não existir, cria)
if '@app.get("/historico_custo_pessoal")' not in c:
    rota_historico = r'''
@app.get("/historico_custo_pessoal")
def get_historico_custo_pessoal():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, periodo, data_criacao FROM historico_custo_pessoal ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data": r[2]} for r in rows]
'''
    if 'if __name__ == "__main__":' in c:
        c = c.replace('if __name__ == "__main__":', rota_historico + '\nif __name__ == "__main__":')
    else:
        c += "\n" + rota_historico

open('main.py', 'w', encoding='utf-8').write(c)
print('[OK] Rotas analise_custo_pessoal e historico restauradas!')
