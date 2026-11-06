import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_back_just_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Verifica se o Request está importado no topo
if "Request" not in c.split("\n")[0:50]:
    print("[AVISO] 'Request' pode não estar importado. Tentando adicionar...")
    # Tenta adicionar Request ao import do FastAPI
    c = c.replace("from fastapi import", "from fastapi import Request,", 1)

# Localiza a rota @app.post("/salvar_integridade_matriz/{periodo}")
idx = c.find('@app.post("/salvar_integridade_matriz/{periodo}")')
if idx == -1:
    print("[ERRO] Rota salvar_integridade_matriz não encontrada. Tentando outra variação...")
    idx = c.find("def salvar_integridade_matriz")

if idx == -1:
    print("[ERRO FATAL] Não foi possível encontrar a rota para substituir.")
    exit(1)

# Encontra o início da função (a linha do def)
start_def = c.find("async def", idx)
if start_def == -1:
    start_def = c.find("def", idx)

# Encontra o fim da função (próximo @app)
fim = c.find("@app", start_def + 10)
if fim == -1:
    fim = len(c)

bloco_antigo = c[start_def:fim]

# Monta o novo bloco (lendo o JSON e salvando no banco)
bloco_novo = '''async def salvar_integridade_matriz(periodo: str, request: Request):
    # Tenta ler as justificativas do corpo da requisição
    try:
        body = await request.json()
        justificativas = body.get("justificativas", {})
    except Exception:
        justificativas = {}

    # Busca a matriz atual do banco para salvar junto
    import sqlite3
    import json
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Se a tabela não tiver coluna de justificativas, criamos ou usamos o resultado_json
    # Para não quebrar o banco, vamos salvar tudo como um JSON único na tabela existente
    cursor.execute("SELECT id, resultado_json FROM historico_integridade_matriz WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))
    row = cursor.fetchone()
    
    if row:
        # Atualiza o resultado_json com as justificativas anexadas
        id_hist, res_json = row
        try:
            dados = json.loads(res_json) if res_json else {}
        except:
            dados = {}
            
        dados["justificativas"] = justificativas
        
        cursor.execute("UPDATE historico_integridade_matriz SET resultado_json = ? WHERE id = ?", (json.dumps(dados), id_hist))
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": "Justificativas salvas."}
    else:
        conn.close()
        return {"ok": False, "mensagem": "Nenhum histórico encontrado para este período. Verifique e salve a matriz primeiro."}
        
'''

c_novo = c[:start_def] + bloco_novo + c[fim:]
open(back_path, "w", encoding="utf-8").write(c_novo)

# Valida a sintaxe
try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Backend alterado com sucesso e sintaxe validada!")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_back_just_{ts}", back_path)
    print("[OK] Backup restaurado.")
