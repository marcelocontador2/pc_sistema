import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_upload_final_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# 1. Remove a rota de upload antiga (para evitar lixo)
padrao_upload = re.compile(r'@app\.post\("/api/configuracoes/logo"\).*?(?=@app\.|# ===|if __name__)', re.DOTALL)
c = padrao_upload.sub('', c)

# 2. Adiciona a rota nova, correta e robusta
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
        f.write(await file.read())
    
    # Atualiza o banco (garante que a coluna existe)
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Cria a tabela se nao existir
    cursor.execute("""CREATE TABLE IF NOT EXISTS configuracoes_entidade (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        razao_social TEXT, nome_fantasia TEXT, cnpj TEXT, endereco TEXT,
        email TEXT, telefone TEXT, contador_nome TEXT, contador_crc TEXT,
        contador_uf TEXT, contador_cpf TEXT, contador_email TEXT, data_atualizacao TEXT
    )""")
    conn.commit()
    
    # Garante que a coluna logo_path existe
    try:
        cursor.execute("ALTER TABLE configuracoes_entidade ADD COLUMN logo_path TEXT DEFAULT ''")
        conn.commit()
    except Exception:
        pass
    
    # Remove a logo antiga do disco (se existir)
    try:
        cursor.execute("SELECT logo_path FROM configuracoes_entidade ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row and row[0]:
            # row[0] pode ser o nome do arquivo ou o caminho completo
            antigo = row[0]
            if not os.path.isabs(antigo):
                antigo = os.path.join(pasta_logos, antigo)
            if os.path.exists(antigo):
                os.remove(antigo)
    except Exception:
        pass
    
    # Insere ou atualiza o registro (salva o NOME do arquivo, nao o caminho completo)
    cursor.execute("SELECT COUNT(*) FROM configuracoes_entidade")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO configuracoes_entidade (razao_social, logo_path) VALUES ('', ?)", (nome_arquivo,))
    else:
        cursor.execute("UPDATE configuracoes_entidade SET logo_path = ?", (nome_arquivo,))
    conn.commit()
    conn.close()
    
    return {"ok": True, "mensagem": "Logo enviada com sucesso!", "logo_path": nome_arquivo}

@app.get("/api/configuracoes/migrar_logo")
async def migrar_logo():
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE configuracoes_entidade ADD COLUMN logo_path TEXT DEFAULT ''")
        conn.commit()
        msg = "Coluna logo_path adicionada."
    except Exception as e:
        msg = "Coluna ja existe ou erro: " + str(e)[:50]
    conn.close()
    return {"ok": True, "mensagem": msg}

'''

# Insere o bloco antes do if __name__
idx = c.find("if __name__")
if idx == -1:
    idx = len(c)
c = c[:idx] + bloco_upload + c[idx:]

open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Backend corrigido: rota de upload reescrita e migracao adicionada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_upload_final_{ts}", back_path)
    print("[OK] Backup restaurado.")
