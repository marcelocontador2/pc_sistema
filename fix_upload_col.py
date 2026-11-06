import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_fix_upload_col_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

idx = c.find('async def upload_logo(')
if idx == -1:
    print("[ERRO] Rota upload_logo nao encontrada.")
    exit(1)

fim = c.find('@app', idx + 10)
if fim == -1:
    fim = len(c)

bloco_novo = '''async def upload_logo(file: UploadFile = File(...)):
    import os, uuid, sqlite3
    from fastapi import HTTPException
    
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in ["png", "jpg", "jpeg"]:
        raise HTTPException(status_code=400, detail="Formato invalido. Use PNG ou JPG.")
    
    pasta_logos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_logos")
    os.makedirs(pasta_logos, exist_ok=True)
    
    nome_arquivo = f"logo_{uuid.uuid4().hex[:8]}.{ext}"
    caminho = os.path.join(pasta_logos, nome_arquivo)
    
    with open(caminho, "wb") as f:
        f.write(await file.read())
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS configuracoes_entidade (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        razao_social TEXT, nome_fantasia TEXT, cnpj TEXT, endereco TEXT,
        email TEXT, telefone TEXT, contador_nome TEXT, contador_crc TEXT,
        contador_uf TEXT, contador_cpf TEXT, contador_email TEXT, data_atualizacao TEXT, logo_path TEXT
    )""")
    conn.commit()
    
    try:
        cursor.execute("ALTER TABLE configuracoes_entidade ADD COLUMN logo_path TEXT DEFAULT ''")
        conn.commit()
    except Exception:
        pass
    
    cursor.execute("SELECT COUNT(*) FROM configuracoes_entidade")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO configuracoes_entidade (razao_social, logo_path) VALUES ('', ?)", (nome_arquivo,))
    else:
        cursor.execute("UPDATE configuracoes_entidade SET logo_path = ?", (nome_arquivo,))
    conn.commit()
    conn.close()
    
    return {"ok": True, "mensagem": "Logo enviada com sucesso!", "logo_path": nome_arquivo}

'''

c = c[:idx] + bloco_novo + c[fim:]
open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Rota de upload reescrita com sucesso e sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_fix_upload_col_{ts}", back_path)
    print("[OK] Backup restaurado.")
