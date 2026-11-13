import sqlite3, json
conn = sqlite3.connect("pc_storage/banco_dados.db")
cur = conn.cursor()
cur.execute("SELECT resultado_json FROM historico_relatorio_consolidado WHERE id = 25")
row = cur.fetchone()
conn.close()
if row:
    dados = json.loads(row[0]).get("dados", [])
    for m in dados:
        nome = str(m.get("nome", ""))
        if "Receita" in nome or "Despesa" in nome:
            print(f"\n--- MÓDULO: {nome} (id={m.get('id')}) ---")
            # Busca os dados reais no PostgreSQL
            try:
                import psycopg2
                PG_CONFIG = {"host": "localhost", "port": 5433, "database": "pc_database", "user": "postgres", "password": "pc_admin_2026"}
                pg = psycopg2.connect(**PG_CONFIG)
                cur_pg = pg.cursor()
                # Identifica a tabela correta
                tabela = "historico_comparativo_receitas" if "Receitas" in nome else "historico_comparativo_despesas"
                coluna = "dados_json" if "Comparativo" in nome else "resultado_json"
                cur_pg.execute(f"SELECT {coluna} FROM {tabela} WHERE id = %s", (m.get('id'),))
                r = cur_pg.fetchone()
                pg.close()
                if r:
                    d = json.loads(r[0])
                    print(f"Chaves: {list(d.keys())}")
                    if "dados" in d:
                        print(f"Tipo de 'dados': {type(d['dados'])}")
                        print(json.dumps(d["dados"], indent=2, ensure_ascii=False)[:800])
                    else:
                        print(json.dumps(d, indent=2, ensure_ascii=False)[:800])
            except Exception as e:
                print(f"Erro ao buscar dados: {e}")
