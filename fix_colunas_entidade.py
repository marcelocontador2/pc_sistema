import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_fix_colunas_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Localiza a rota obter_entidade
idx = c.find('async def obter_entidade():')
if idx == -1:
    print("[ERRO] Rota obter_entidade nao encontrada.")
    exit(1)

# Encontra o final da funcao
fim = c.find('@app', idx + 10)
if fim == -1:
    fim = len(c)

# Nova funcao usando DictCursor para pegar pelos nomes das colunas (sem erro de indice)
bloco_novo = '''async def obter_entidade():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row # Permite acessar colunas pelo nome
    cursor = conn.cursor()
    
    # Cria a tabela se nao existir
    cursor.execute("""CREATE TABLE IF NOT EXISTS configuracoes_entidade (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        razao_social TEXT, nome_fantasia TEXT, cnpj TEXT, endereco TEXT,
        email TEXT, telefone TEXT, contador_nome TEXT, contador_crc TEXT,
        contador_uf TEXT, contador_cpf TEXT, contador_email TEXT, data_atualizacao TEXT, logo_path TEXT
    )""")
    conn.commit()
    
    cursor.execute("SELECT * FROM configuracoes_entidade ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"razao_social": "", "nome_fantasia": "", "cnpj": "", "endereco": "", "email": "", "telefone": "", "contador_nome": "", "contador_crc": "", "contador_uf": "", "contador_cpf": "", "contador_email": "", "logo_path": ""}
    
    # Acessa pelo nome da coluna (evita erro de indice desalinhado)
    def get_col(nome):
        try:
            return row[nome] or ""
        except Exception:
            return ""
            
    return {
        "razao_social": get_col("razao_social"),
        "nome_fantasia": get_col("nome_fantasia"),
        "cnpj": get_col("cnpj"),
        "endereco": get_col("endereco"),
        "email": get_col("email"),
        "telefone": get_col("telefone"),
        "contador_nome": get_col("contador_nome"),
        "contador_crc": get_col("contador_crc"),
        "contador_uf": get_col("contador_uf"),
        "contador_cpf": get_col("contador_cpf"),
        "contador_email": get_col("contador_email"),
        "logo_path": get_col("logo_path")
    }

'''

c = c[:idx] + bloco_novo + c[fim:]
open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Rota obter_entidade reescrita com sqlite3.Row (mapeamento por nome) e sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_fix_colunas_{ts}", back_path)
    print("[OK] Backup restaurado.")
