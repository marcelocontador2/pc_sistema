import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_fix_logo_vis_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# 1. Ajusta a rota GET da entidade para tentar ler o banco, mas se falhar, pega o arquivo mais recente da pasta
idx = c.find('async def obter_entidade():')
if idx != -1:
    fim = c.find('@app', idx + 10)
    if fim == -1: fim = idx + 2000
    
    bloco_novo = '''async def obter_entidade():
    import sqlite3, os, glob
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS configuracoes_entidade (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        razao_social TEXT, nome_fantasia TEXT, cnpj TEXT, endereco TEXT,
        email TEXT, telefone TEXT, contador_nome TEXT, contador_crc TEXT,
        contador_uf TEXT, contador_cpf TEXT, contador_email TEXT, data_atualizacao TEXT, logo_path TEXT
    )""")
    cursor.execute("SELECT * FROM configuracoes_entidade ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    # Fallback: se nao tiver logo no banco, procura o arquivo mais recente na pasta
    logo = ""
    if row and len(row) > 12 and row[12]:
        logo = row[12]
    else:
        pasta_logos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_logos")
        if os.path.exists(pasta_logos):
            arquivos = glob.glob(os.path.join(pasta_logos, "*.*"))
            if arquivos:
                # Pega o mais recente
                recente = max(arquivos, key=os.path.getmtime)
                logo = os.path.basename(recente)
    
    if not row:
        return {"razao_social": "", "nome_fantasia": "", "cnpj": "", "endereco": "", "email": "", "telefone": "", "contador_nome": "", "contador_crc": "", "contador_uf": "", "contador_cpf": "", "contador_email": "", "logo_path": logo}
    
    return {
        "razao_social": row[1] or "", "nome_fantasia": row[2] or "", "cnpj": row[3] or "",
        "endereco": row[4] or "", "email": row[5] or "", "telefone": row[6] or "",
        "contador_nome": row[7] or "", "contador_crc": row[8] or "", "contador_uf": row[9] or "",
        "contador_cpf": row[10] or "", "contador_email": row[11] or "", "logo_path": logo
    }

'''
    c = c[:idx] + bloco_novo + c[fim:]
    print("[OK] Rota GET ajustada para fallback de pasta.")

# 2. Garante que o mount /static_logos esta correto
if "/static_logos" not in c:
    c = "from fastapi.staticfiles import StaticFiles\n" + c
    c += '\napp.mount("/static_logos", StaticFiles(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_logos")), name="static_logos")\n'
    print("[OK] Mount /static_logos adicionado.")
else:
    print("[OK] Mount /static_logos ja existe.")

open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Backend ajustado e sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_fix_logo_vis_{ts}", back_path)
