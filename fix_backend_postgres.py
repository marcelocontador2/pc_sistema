import os
import re

caminho_main = "pc_backend/main.py"

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Substitui o bloco inteiro de rotas de integridade (da rota calcular até a excluir)
inicio_rotas = conteudo.find('@app.get("/api/integridade_matriz/{periodo}")')
fim_rotas = conteudo.find('@app.get("/gerar_pdf_conferencia/{id}")')

if inicio_rotas != -1 and fim_rotas != -1:
    novo_bloco_backend = '''@app.get("/api/integridade_matriz/{periodo}")
async def api_integridade_matriz_calcular(periodo: str):
    try:
        from .matriz_integridade import gerar_matriz
        dados = gerar_matriz(periodo)
        return dados
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}

@app.post("/api/integridade_matriz/{periodo}/salvar")
async def salvar_integridade_matriz(periodo: str, request: Request):
    import json
    from datetime import datetime
    try:
        body = await request.json()
        # Recebe a matriz enviada pelo frontend
        matriz = body.get("matriz", [])
        justificativas = body.get("justificativas", {})
        
        dados_matriz = {
            "periodo": periodo,
            "matriz": matriz,
            "justificativas": justificativas
        }
        
        data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Cria a tabela se não existir no Postgres
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_integridade_matriz (
                id SERIAL PRIMARY KEY, 
                periodo TEXT, 
                data_geracao TEXT, 
                resultado_json TEXT
            )
        """)
        
        cursor.execute(
            "INSERT INTO historico_integridade_matriz (periodo, data_geracao, resultado_json) VALUES (%s, %s, %s)",
            (periodo, data_agora, json.dumps(dados_matriz, ensure_ascii=False))
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"ok": True, "mensagem": "Matriz salva com sucesso no PostgreSQL!"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}

@app.get("/historico_integridade_matriz")
def listar_integridade_matriz():
    import json
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, periodo, data_geracao, resultado_json FROM historico_integridade_matriz ORDER BY id DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        resultado = []
        for r in rows:
            resultado.append({
                "id": r[0],
                "periodo": r[1],
                "data_geracao": r[2],
                "dados": r[3]
            })
        return Response(content=json.dumps(resultado), media_type="application/json")
    except Exception as e:
        return Response(content=json.dumps({"erro": True, "mensagem": str(e)}), media_type="application/json")

@app.get("/historico_integridade_matriz/{id}")
async def buscar_integridade_matriz(id: int):
    import json
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT resultado_json FROM historico_integridade_matriz WHERE id = %s", (id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row: 
            raise HTTPException(status_code=404, detail="Não encontrado")
        return json.loads(row[0])
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}

@app.post("/excluir_multiplos_integridade_matriz")
async def excluir_integridade_matriz(request: Request):
    try:
        body = await request.json()
        ids = body.get("ids", [])
        if not ids:
            return {"ok": False, "mensagem": "Nenhum ID fornecido."}
            
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Formata os IDs para o IN do SQL
        placeholders = ','.join(['%s'] * len(ids))
        cursor.execute(f"DELETE FROM historico_integridade_matriz WHERE id IN ({placeholders})", tuple(ids))
        
        conn.commit()
        cursor.close()
        conn.close()
        return {"ok": True, "mensagem": "Excluído com sucesso!"}
    except Exception as e:
        return {"ok": False, "mensagem": str(e)}

'''
    # Substitui as rotas antigas pelas novas
    conteudo = conteudo[:inicio_rotas] + novo_bloco_backend + conteudo[fim_rotas:]

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)
print("✅ Backend (main.py) atualizado para PostgreSQL e rota /salvar criada!")
