import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_force_save_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Acha a rota de salvar matriz
idx = c.find('@app.post("/salvar_integridade_matriz/{periodo}")')
if idx == -1:
    print("[ERRO] Rota nao encontrada.")
    exit(1)

# Pega a funcao inteira (do def ate a proxima rota @app)
start_def = c.find("async def salvar_integridade_matriz", idx)
fim = c.find("@app", start_def + 10)
if fim == -1:
    fim = len(c)

# Nova funcao robusta: Pega a matriz gerada e INSERE um novo registro no historico com as justificativas
bloco_novo = '''async def salvar_integridade_matriz(periodo: str, request: Request):
    import sqlite3
    import json
    from datetime import datetime

    try:
        body = await request.json()
        justificativas = body.get("justificativas", {})
    except Exception:
        justificativas = {}

    # Pega a matriz de novo (para garantir que estamos salvando os dados atuais)
    # Chama a funcao que gera a matriz (que ja existe no seu codigo)
    try:
        dados_matriz = await api_integridade_matriz(periodo)
    except Exception:
        return {"ok": False, "mensagem": "Erro ao gerar a matriz para salvar."}

    # Adiciona as justificativas ao JSON da matriz
    dados_matriz["justificativas"] = justificativas

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Cria a tabela se nao existir (garantia)
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_integridade_matriz (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")

    data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insere um NOVO registro no historico
    cursor.execute(
        "INSERT INTO historico_integridade_matriz (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
        (periodo, data_agora, json.dumps(dados_matriz, ensure_ascii=False))
    )
    
    conn.commit()
    conn.close()

    return {"ok": True, "mensagem": "Matriz e justificativas salvas com sucesso!"}
'''

c_novo = c[:start_def] + bloco_novo + c[fim:]
open(back_path, "w", encoding="utf-8").write(c_novo)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Backend alterado com sucesso! A funcao agora insere um novo historico.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_force_save_{ts}", back_path)
