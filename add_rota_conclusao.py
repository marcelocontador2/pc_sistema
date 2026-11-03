import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_salvar_conclusao_{ts}")

c = open(back_path, encoding='utf-8-sig').read()

# Verifica se a rota já existe para não duplicar
if "/salvar_conclusao_centro_custos/" not in c:
    nova_rota = '''
@app.post("/salvar_conclusao_centro_custos/{historico_id}")
async def salvar_conclusao_centro_custos(historico_id: int, request: Request):
    import sqlite3, json, os
    try:
        data = await request.json()
        texto = data.get("texto", "")
        
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT dados_json FROM historico_centro_custos WHERE id = ?", (historico_id,))
        row = cur.fetchone()
        
        if row:
            dados = json.loads(row[0])
            dados["conclusao_personalizada"] = texto
            cur.execute("UPDATE historico_centro_custos SET dados_json = ? WHERE id = ?", (json.dumps(dados), historico_id))
            conn.commit()
            conn.close()
            return {"erro": False, "mensagem": "Conclusão salva com sucesso!"}
        
        conn.close()
        return {"erro": True, "mensagem": "Histórico não encontrado."}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
'''
    # Adiciona a rota no final do arquivo
    c += nova_rota
    
    # Garante que a importação do Request do FastAPI está no topo
    if "from fastapi import Request" not in c and "from fastapi import" in c:
        c = c.replace("from fastapi import", "from fastapi import Request,", 1)
    elif "from fastapi import Request" not in c:
        c = "from fastapi import Request\n" + c

    open(back_path, 'w', encoding='utf-8').write(c)
    print("[OK] Rota de Salvar Conclusão criada no Backend!")
else:
    print("[AVISO] Rota já existia no Backend.")

try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe: {e}")
