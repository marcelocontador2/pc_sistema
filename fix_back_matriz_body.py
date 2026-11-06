import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_matriz_body_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Encontra a funcao de salvar
idx = c.find("async def salvar_integridade_matriz")
if idx == -1:
    print("[ERRO] Funcao nao encontrada.")
    exit(1)

fim = c.find("@app", idx + 10)
if fim == -1:
    fim = len(c)

# Nova funcao: recebe a matriz do body, sem chamar api_integridade_matriz
bloco_novo = '''async def salvar_integridade_matriz(periodo: str, request: Request):
    import sqlite3
    import json
    from datetime import datetime

    try:
        body = await request.json()
        justificativas = body.get("justificativas", {})
        matriz = body.get("matriz", [])
    except Exception:
        justificativas = {}
        matriz = []

    if not matriz:
        return {"ok": False, "mensagem": "Matriz vazia. Clique em 'Verificar Matriz' antes de salvar."}

    # Monta o JSON final com a matriz e as justificativas
    dados_matriz = {
        "matriz": matriz,
        "justificativas": justificativas
    }

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_integridade_matriz (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")

    data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO historico_integridade_matriz (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
        (periodo, data_agora, json.dumps(dados_matriz, ensure_ascii=False))
    )
    
    conn.commit()
    conn.close()

    return {"ok": True, "mensagem": "Matriz e justificativas salvas com sucesso!"}
'''

c_novo = c[:idx] + bloco_novo + c[fim:]
open(back_path, "w", encoding="utf-8").write(c_novo)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Backend alterado e sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_matriz_body_{ts}", back_path)
    print("[OK] Backup restaurado.")
