import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_migra_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# 1. Remove a rota antiga de migracao (se existir) para recriar limpa
import re
c = re.sub(r'@app\.get\("/api/configuracoes/migrar_logo"\).*?return \{"ok": True, "mensagem": "Migracao verificada\."\}', '', c, flags=re.DOTALL)

# 2. Adiciona a rota de migracao no final do arquivo
bloco_migra = '''

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
        msg = f"Ja existe ou erro: {str(e)[:50]}"
    conn.close()
    return {"ok": True, "mensagem": msg}

'''
idx = c.find("if __name__")
if idx == -1:
    idx = len(c)
c = c[:idx] + bloco_migra + c[idx:]

# 3. Corrige a rota de upload: garante que a tabela e a coluna existem ANTES do UPDATE
# Procura a rota de upload e adiciona a criacao/migracao interna
antigo_upload = '''    pasta_logos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_logos")
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
    cursor.execute("UPDATE configuracoes_entidade SET logo_path = ?", (caminho,))'''

novo_upload = '''    pasta_logos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_logos")
    os.makedirs(pasta_logos, exist_ok=True)
    nome_arquivo = f"logo_{uuid.uuid4().hex[:8]}.{ext}"
    caminho = os.path.join(pasta_logos, nome_arquivo)
    with open(caminho, "wb") as f:
        f.write(await file.read())
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Garante que a tabela existe
    cursor.execute("""CREATE TABLE IF NOT EXISTS configuracoes_entidade (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        razao_social TEXT, nome_fantasia TEXT, cnpj TEXT, endereco TEXT,
        email TEXT, telefone TEXT, contador_nome TEXT, contador_crc TEXT,
        contador_uf TEXT, contador_cpf TEXT, contador_email TEXT, data_atualizacao TEXT,
        logo_path TEXT
    )""")
    conn.commit()
    
    # Garante que a coluna logo_path existe (para tabelas antigas)
    try:
        cursor.execute("ALTER TABLE configuracoes_entidade ADD COLUMN logo_path TEXT DEFAULT ''")
        conn.commit()
    except Exception:
        pass
    
    # Se nao houver registro, insere um vazio
    cursor.execute("SELECT COUNT(*) FROM configuracoes_entidade")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO configuracoes_entidade (razao_social, logo_path) VALUES ('', ?)", (caminho,))
    else:
        cursor.execute("UPDATE configuracoes_entidade SET logo_path = ?", (caminho,))
    conn.commit()'''

if antigo_upload in c:
    c = c.replace(antigo_upload, novo_upload, 1)
    print("[OK] Rota de upload corrigida (cria tabela e coluna antes do UPDATE).")
else:
    print("[AVISO] Trecho exato da rota de upload nao encontrado.")

open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_migra_{ts}", back_path)
    print("[OK] Backup restaurado.")
