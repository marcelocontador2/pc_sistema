import re, sqlite3, os

print("=" * 70)
print("AUDITORIA DE ROTAS E HISTÓRICOS DO SISTEMA")
print("=" * 70)

# 1. Auditoria do main.py
with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

print("\n[1] ROTAS DE GERAÇÃO DE ARQUIVO (PDF, WORD, EXCEL)")
print("-" * 70)
rotas_gerar = re.findall(r'@app\.get\("(/gerar[^"]*)"\)', codigo)
for r in sorted(set(rotas_gerar)):
    print(f"  {r}")

print("\n[2] ROTAS DE DOWNLOAD")
print("-" * 70)
rotas_down = re.findall(r'@app\.get\("(/download[^"]*)"\)', codigo)
for r in sorted(set(rotas_down)):
    print(f"  {r}")

print("\n[3] ROTAS DE API DE ANÁLISE")
print("-" * 70)
rotas_api = re.findall(r'@app\.get\("(/api/analise[^"]*)"\)', codigo)
for r in sorted(set(rotas_api)):
    print(f"  {r}")

# 2. Auditoria do banco de dados
print("\n" + "=" * 70)
print("[4] ESTRUTURA DAS TABELAS DE HISTÓRICO")
print("=" * 70)

db_path = os.path.join("pc_storage", "banco_dados.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'historico_%' ORDER BY name")
tabelas = cursor.fetchall()

for (tab,) in tabelas:
    cursor.execute(f"PRAGMA table_info({tab})")
    colunas = [c[1] for c in cursor.fetchall()]
    print(f"\n  Tabela: {tab}")
    print(f"  Colunas: {', '.join(colunas)}")

# 3. Verifica quais tabelas tem dados para o período 2026-TRIMESTRE-3
print("\n" + "=" * 70)
print("[5] DADOS DISPONÍVEIS PARA 2026-TRIMESTRE-3")
print("=" * 70)

periodo = "2026-TRIMESTRE-3"
for (tab,) in tabelas:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {tab} WHERE periodo LIKE ?", (f"%{periodo}%",))
        count = cursor.fetchone()[0]
        if count > 0:
            cursor.execute(f"SELECT id, data_geracao FROM {tab} WHERE periodo LIKE ? ORDER BY id DESC LIMIT 1", (f"%{periodo}%",))
            row = cursor.fetchone()
            print(f"  ✓ {tab}: {count} registros (último ID: {row[0]}, data: {row[1]})")
    except Exception as e:
        pass

conn.close()
print("\n" + "=" * 70)
print("FIM DA AUDITORIA")
print("=" * 70)
