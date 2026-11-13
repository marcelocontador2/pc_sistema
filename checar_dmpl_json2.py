import sqlite3, json
conn = sqlite3.connect("pc_storage/banco_dados.db")
cur = conn.cursor()
cur.execute("SELECT id, resultado_json FROM historico_relatorio_consolidado WHERE id = 24")
row = cur.fetchone()
conn.close()

if row:
    dados = json.loads(row[1])
    print("=== ESTRUTURA DE 'dados' ===")
    d = dados.get("dados")
    print(f"Tipo de 'dados': {type(d)}")
    
    if isinstance(d, list):
        print(f"Quantidade de itens: {len(d)}")
        print("Primeiros 5 itens:")
        for i, item in enumerate(d[:5]):
            print(f"  [{i}] Tipo: {type(item)} -> {str(item)[:150]}")
    elif isinstance(d, dict):
        print(f"Chaves de 'dados': {list(d.keys())[:10]}")
        for k, v in list(d.items())[:2]:
            print(f"  {k}: {type(v)} -> {str(v)[:150]}")
