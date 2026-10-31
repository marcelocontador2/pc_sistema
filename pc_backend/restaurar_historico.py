import re

c = open('main.py', encoding='utf-8-sig').read()

# 1. Remove a rota do histórico antiga (vazia)
padrao = r'@app\.get\("/historico_custo_pessoal"\)\s*\n\s*(async\s+)?def listar_historico_custo_pessoal\(\):\s*\n(\s*\n)*'
c = re.sub(padrao, '', c)

# 2. Insere a nova rota funcional antes do if __name__
nova_rota = r'''
@app.get("/historico_custo_pessoal")
async def listar_historico_custo_pessoal():
    import sqlite3, os
    from fastapi.responses import JSONResponse
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, periodo, data_geracao FROM historico_custo_pessoal ORDER BY id DESC")
        rows = cur.fetchall()
        return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]
    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)
    finally:
        conn.close()
'''

if 'if __name__ == "__main__":' in c:
    c = c.replace('if __name__ == "__main__":', nova_rota + '\nif __name__ == "__main__":')
else:
    c += "\n" + nova_rota

open('main.py', 'w', encoding='utf-8').write(c)
print('[OK] Rota do histórico restaurada!')
