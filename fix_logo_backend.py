import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_logo_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Verifica se a rota de upload ja existe
if "/api/configuracoes/logo" in c:
    print("[AVISO] Rota de upload de logo ja existe.")
else:
    bloco = '''
@app.post("/api/configuracoes/logo")
async def upload_logo(file: UploadFile = File(...)):
    import os, uuid, sqlite3
    from fastapi import HTTPException
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in ["png", "jpg", "jpeg"]:
        raise HTTPException(status_code=400, detail="Formato invalido.")
    pasta_logos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_logos")
    os.makedirs(pasta_logos, exist_ok=True)
    nome_arquivo = f"logo_{uuid.uuid4().hex[:8]}.{ext}"
    caminho = os.path.join(pasta_logos, nome_arquivo)
    with open(caminho, "wb") as f:
        f.write(await file.read())
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Garante que a coluna existe
    try:
        cursor.execute("ALTER TABLE configuracoes_entidade ADD COLUMN logo_path TEXT DEFAULT ''")
    except: pass
    cursor.execute("UPDATE configuracoes_entidade SET logo_path = ?", (caminho,))
    conn.commit()
    conn.close()
    return {"ok": True, "mensagem": "Logo enviada!"}

'''
    # Insere antes do if __name__
    idx = c.find("if __name__")
    if idx == -1: idx = len(c)
    c = c[:idx] + bloco + c[idx:]
    
    # Adiciona UploadFile e File ao import se necessario
    if "UploadFile" not in c.split("\n")[0:50]:
        c = c.replace("from fastapi import FastAPI", "from fastapi import FastAPI, UploadFile, File", 1)
    
    open(back_path, "w", encoding="utf-8").write(c)
    try:
        ast.parse(open(back_path, encoding="utf-8").read())
        print("[OK] Rota de upload da logo adicionada e sintaxe validada.")
    except SyntaxError as e:
        print(f"[ERRO] Sintaxe quebrada: {e}")
        shutil.copy2(f"{back_path}.bak_logo_{ts}", back_path)

# Adiciona mount para servir as logos
if "/static_logos" not in c:
    c = open(back_path, encoding="utf-8-sig").read()
    c = c + '\napp.mount("/static_logos", StaticFiles(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_logos")), name="static_logos")\n'
    if "from fastapi.staticfiles import StaticFiles" not in c:
        c = "from fastapi.staticfiles import StaticFiles\n" + c
    open(back_path, "w", encoding="utf-8").write(c)
    print("[OK] Mount /static_logos adicionado.")
