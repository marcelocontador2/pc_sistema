import psycopg2
import json

PG_CONFIG = {
    "host": "localhost", "port": 5433,
    "database": "pc_database", "user": "postgres", "password": "pc_admin_2026",
}

try:
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()

    print("🔍 BUSCANDO O JSON DO HISTÓRICO DE 04/11/2026...\n")

    # Procura em todas as tabelas de histórico
    tabelas = ["historico_integridade_matriz", "historico_matriz_integridade", "historico_integridade"]
    
    for t in tabelas:
        try:
            cursor.execute(f"SELECT id, periodo, data_geracao, resultado_json FROM {t} WHERE data_geracao LIKE '%2026-11-04%' ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                print(f"✅ ENCONTRADO NA TABELA: {t}")
                print(f"   ID: {row[0]} | Período: {row[1]} | Data: {row[2]}")
                print(f"\n📄 JSON SALVO:\n")
                dados = json.loads(row[3])
                print(json.dumps(dados, indent=2, ensure_ascii=False))
                break
        except Exception as e:
            pass
    else:
        print("❌ Nenhum registro de 04/11/2026 encontrado nas tabelas de histórico.")
        print("Buscando o registro mais antigo disponível...")
        for t in tabelas:
            try:
                cursor.execute(f"SELECT id, periodo, data_geracao, resultado_json FROM {t} ORDER BY id ASC LIMIT 1")
                row = cursor.fetchone()
                if row:
                    print(f"✅ Registro mais antigo na tabela {t}:")
                    print(f"   ID: {row[0]} | Período: {row[1]} | Data: {row[2]}")
                    dados = json.loads(row[3])
                    print(json.dumps(dados, indent=2, ensure_ascii=False))
                    break
            except:
                pass

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ ERRO: {e}")
