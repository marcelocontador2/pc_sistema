from pathlib import Path
import sqlite3
import ast

# ============ 1. CRIAR A TABELA NO SQLITE ============
DB_PATH = Path("..") / "pc_storage" / "banco_dados.db"
print(f"Banco: {DB_PATH.absolute()}")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Criar tabela
cur.execute("""
    CREATE TABLE IF NOT EXISTS configuracoes (
        chave TEXT PRIMARY KEY,
        valor TEXT NOT NULL,
        data_atualizacao TEXT
    )
""")
print("OK: Tabela 'configuracoes' criada/verificada.")

# Inserir valor padrao se nao existir
cur.execute("SELECT valor FROM configuracoes WHERE chave = 'tipo_entidade'")
row = cur.fetchone()
if not row:
    cur.execute(
        "INSERT INTO configuracoes (chave, valor, data_atualizacao) VALUES (?, ?, datetime('now'))",
        ("tipo_entidade", "COFEN")
    )
    print("OK: Valor padrao 'tipo_entidade = COFEN' inserido.")
else:
    print(f"OK: Valor atual de tipo_entidade: {row[0]}")

conn.commit()
conn.close()

# ============ 2. ADICIONAR ENDPOINTS NO main.py ============
arquivo = Path("main.py")
conteudo = arquivo.read_text(encoding="utf-8")

# Verificar se os endpoints ja existem
if "/api/configuracoes" in conteudo:
    print("AVISO: Endpoints /api/configuracoes ja existem no main.py")
else:
    # Encontrar um lugar seguro para inserir (depois do app = FastAPI(...))
    alvo = 'app = FastAPI(title="PC - Prestacao de Contas API")'
    if alvo not in conteudo:
        print("ERRO: nao achei o app = FastAPI(...)")
        exit(1)

    # Bloco de endpoints
    bloco_endpoints = '''

# === CONFIGURACOES GLOBAIS (31/10/2026) ===
@app.get("/api/configuracoes")
async def get_configuracoes():
    """Retorna as configuracoes globais (tipo_entidade: COFEN ou COREN)."""
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT chave, valor FROM configuracoes")
    rows = cur.fetchall()
    conn.close()
    return {k: v for k, v in rows}


@app.post("/api/configuracoes")
async def post_configuracoes(config: dict):
    """Salva as configuracoes globais. Ex: {"tipo_entidade": "COREN"}."""
    import sqlite3, os, datetime
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for chave, valor in config.items():
        cur.execute(
            "INSERT OR REPLACE INTO configuracoes (chave, valor, data_atualizacao) VALUES (?, ?, ?)",
            (chave, str(valor), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
    conn.commit()
    conn.close()
    return {"status": "ok", "configuracoes": config}
'''

    # Inserir depois do app = FastAPI(...)
    conteudo = conteudo.replace(alvo, alvo + bloco_endpoints, 1)
    print("OK: Endpoints /api/configuracoes adicionados ao main.py")

    arquivo.write_text(conteudo, encoding="utf-8")

    # Validar sintaxe
    try:
        ast.parse(conteudo)
        print("Sintaxe OK!")
    except SyntaxError as e:
        print(f"ERRO de sintaxe: {e}")

print("\nCommit 1 concluido!")
