import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_logo_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Verifica se a rota de upload ja existe
if "/api/configuracoes/logo" in c:
    print("[AVISO] Rota de upload de logo ja existe. Pulando.")
else:
    # 1. Adiciona coluna 'logo_path' na tabela (se nao existir)
    # Como SQLite nao tem 'ADD COLUMN IF NOT EXISTS', usamos try/except
    bloco_migracao = '''
@app.get("/api/configuracoes/migrar_logo")
async def migrar_logo():
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE configuracoes_entidade ADD COLUMN logo_path TEXT DEFAULT ''")
        conn.commit()
        print("[MIGRACAO] Coluna logo_path adicionada.")
    except Exception as e:
        print(f"[MIGRACAO] Coluna ja existe ou erro: {e}")
    conn.close()
    return {"ok": True, "mensagem": "Migracao verificada."}

'''
    idx = c.find("if __name__")
    if idx == -1:
        idx = len(c)
    c = c[:idx] + bloco_migracao + c[idx:]

    # 2. Rota de upload da logo
    bloco_upload = '''
@app.post("/api/configuracoes/logo")
async def upload_logo(file: UploadFile = File(...)):
    import os, uuid, sqlite3
    from fastapi import HTTPException
    # Valida extensao
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in ["png", "jpg", "jpeg"]:
        raise HTTPException(status_code=400, detail="Formato invalido. Use PNG ou JPG.")
    
    # Pasta de destino
    pasta_logos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_logos")
    os.makedirs(pasta_logos, exist_ok=True)
    
    # Nome unico
    nome_arquivo = f"logo_{uuid.uuid4().hex[:8]}.{ext}"
    caminho = os.path.join(pasta_logos, nome_arquivo)
    
    # Salva o arquivo
    with open(caminho, "wb") as f:
        conteudo = await file.read()
        f.write(conteudo)
    
    # Atualiza o banco (remove logo antiga do disco se existir)
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT logo_path FROM configuracoes_entidade ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    if row and row[0]:
        try:
            os.remove(row[0])
        except Exception:
            pass
    cursor.execute("UPDATE configuracoes_entidade SET logo_path = ?", (caminho,))
    conn.commit()
    conn.close()
    
    return {"ok": True, "mensagem": "Logo enviada com sucesso!", "logo_path": nome_arquivo}

'''
    idx = c.find("if __name__")
    if idx == -1:
        idx = len(c)
    c = c[:idx] + bloco_upload + c[idx:]

    # 3. Ajusta a rota GET para retornar logo_path
    # Procura o "return {'razao_social': row[1]..." e adiciona logo_path
    antigo_get = "return {'razao_social': row[1] or '', 'nome_fantasia': row[2] or '', 'cnpj': row[3] or '', 'endereco': row[4] or '', 'email': row[5] or '', 'telefone': row[6] or '', 'contador_nome': row[7] or '', 'contador_crc': row[8] or '', 'contador_uf': row[9] or '', 'contador_cpf': row[10] or '', 'contador_email': row[11] or ''}"
    novo_get = "return {'razao_social': row[1] or '', 'nome_fantasia': row[2] or '', 'cnpj': row[3] or '', 'endereco': row[4] or '', 'email': row[5] or '', 'telefone': row[6] or '', 'contador_nome': row[7] or '', 'contador_crc': row[8] or '', 'contador_uf': row[9] or '', 'contador_cpf': row[10] or '', 'contador_email': row[11] or '', 'logo_path': row[12] if len(row) > 12 else ''}"
    if antigo_get in c:
        c = c.replace(antigo_get, novo_get, 1)
        print("[OK] Rota GET ajustada para retornar logo_path.")

    # 4. Ajusta o POST para salvar logo_path tambem
    # No POST, o INSERT deve incluir logo_path
    antigo_insert = "cursor.execute('''INSERT INTO configuracoes_entidade\n        (razao_social, nome_fantasia, cnpj, endereco, email, telefone, contador_nome, contador_crc, contador_uf, contador_cpf, contador_email, data_atualizacao)\n        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', ("
    novo_insert = "cursor.execute('''INSERT INTO configuracoes_entidade\n        (razao_social, nome_fantasia, cnpj, endereco, email, telefone, contador_nome, contador_crc, contador_uf, contador_cpf, contador_email, data_atualizacao, logo_path)\n        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', ("
    if antigo_insert in c:
        c = c.replace(antigo_insert, novo_insert, 1)
        # Adiciona o valor no final da tupla
        c = c.replace("        data_agora))", "        data_agora,\n        body.get('logo_path', '')))", 1)
        print("[OK] Rota POST ajustada para salvar logo_path.")

    open(back_path, "w", encoding="utf-8").write(c)
    
    try:
        ast.parse(open(back_path, encoding="utf-8").read())
        print("[OK] Backend atualizado com rotas de logo e sintaxe validada.")
    except SyntaxError as e:
        print(f"[ERRO] Sintaxe quebrada: {e}")
        shutil.copy2(f"{back_path}.bak_logo_{ts}", back_path)
        print("[OK] Backup restaurado.")

# Garante que UploadFile e File estao importados
if "from fastapi import FastAPI" in c and "UploadFile" not in c.split("from fastapi import")[1].split("\n")[0]:
    c = c.replace("from fastapi import FastAPI", "from fastapi import FastAPI, UploadFile, File", 1)
    open(back_path, "w", encoding="utf-8").write(c)
    print("[OK] UploadFile e File adicionados ao import do FastAPI.")
