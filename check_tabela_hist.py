import sqlite3, os

db_path = "pc_storage/banco_dados.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verifica se a tabela existe e a estrutura
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historico_integridade_matriz'")
tabela = cursor.fetchone()

if tabela:
    print("[OK] Tabela 'historico_integridade_matriz' existe.")
    cursor.execute("PRAGMA table_info(historico_integridade_matriz)")
    colunas = cursor.fetchall()
    print("Colunas:")
    for col in colunas:
        print(f"  {col[1]} ({col[2]})")
    
    # Verifica se tem algum registro (mesmo que a query anterior tenha dado vazio, pode ser que a tabela exista e esteja vazia)
    cursor.execute("SELECT COUNT(*) FROM historico_integridade_matriz")
    qtd = cursor.fetchone()[0]
    print(f"\nTotal de registros: {qtd}")
else:
    print("[AVISO] Tabela 'historico_integridade_matriz' NAO existe no banco.")
    print("Tabelas existentes:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for t in cursor.fetchall():
        print(f"  {t[0]}")

conn.close()
