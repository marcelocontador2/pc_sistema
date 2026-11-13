import sqlite3, json
conn = sqlite3.connect("pc_storage/banco_dados.db")
cur = conn.cursor()
cur.execute("SELECT id, periodo, resultado_json FROM historico_relatorio_consolidado ORDER BY id DESC LIMIT 1")
row = cur.fetchone()
conn.close()
if row:
    print(f"ID: {row[0]} | Periodo: {row[1]}")
    dados = json.loads(row[2])
    print("Chaves no JSON:", list(dados.keys()))
    if "dados" in dados:
        print("Modulos salvos:", [m.get("nome_interno") for m in dados["dados"]])
    else:
        print("A chave 'dados' NAO existe no JSON!")
else:
    print("Nenhum relatorio encontrado.")
