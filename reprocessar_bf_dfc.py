import sys, os, json, sqlite3, datetime

# Adiciona o backend ao path para importar as funções
sys.path.insert(0, "pc_backend")
sys.path.insert(0, ".")

# 1. Re-processar o BF
print("=" * 70)
print("RE-PROCESSANDO O BF")
print("=" * 70)
try:
    from app.routers.balanco_financeiro import processar_bf
    
    caminho_csv = os.path.join("pc_storage", "uploads_raw", "BALANCO_FINANCEIRO_2026_TRIMESTRE_3.csv")
    if os.path.exists(caminho_csv):
        resultado = processar_bf(caminho_csv)
        dados_corrigidos = resultado.get("dados", resultado)
        
        # Atualiza o banco
        db_path = os.path.join("pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM historico_analise_financeira_bf ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            id_bf = row[0]
            cursor.execute(
                "UPDATE historico_analise_financeira_bf SET resultado_json = ? WHERE id = ?",
                (json.dumps(dados_corrigidos, ensure_ascii=False), id_bf)
            )
            conn.commit()
            print(f"[OK] BF id={id_bf} atualizado no banco.")
        conn.close()
    else:
        print(f"[AVISO] CSV do BF não encontrado em {caminho_csv}")
except Exception as e:
    print(f"[ERRO] BF: {e}")

# 2. Re-processar o DFC
print("\n" + "=" * 70)
print("RE-PROCESSANDO O DFC")
print("=" * 70)
try:
    from app.routers.dfc import api_analise_dfc
    import asyncio
    
    caminho_csv = os.path.join("pc_storage", "uploads_raw", "DFC_2026_TRIMESTRE_3.csv")
    if os.path.exists(caminho_csv):
        # Chama a API de análise do DFC (é async)
        resultado = asyncio.run(api_analise_dfc("2026-TRIMESTRE-3"))
        
        if isinstance(resultado, dict) and not resultado.get("erro"):
            dados_corrigidos = resultado
            
            # Atualiza o banco
            db_path = os.path.join("pc_storage", "banco_dados.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM historico_analise_dfc ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                id_dfc = row[0]
                cursor.execute(
                    "UPDATE historico_analise_dfc SET resultado_json = ? WHERE id = ?",
                    (json.dumps(dados_corrigidos, ensure_ascii=False), id_dfc)
                )
                conn.commit()
                print(f"[OK] DFC id={id_dfc} atualizado no banco.")
            conn.close()
        else:
            print(f"[AVISO] DFC retornou erro: {resultado.get('erro')}")
    else:
        print(f"[AVISO] CSV do DFC não encontrado em {caminho_csv}")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"[ERRO] DFC: {e}")

# 3. Verificação: confirma se os acentos foram salvos
print("\n" + "=" * 70)
print("VERIFICAÇÃO FINAL")
print("=" * 70)
db_path = os.path.join("pc_storage", "banco_dados.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

for tabela in ["historico_analise_financeira_bf", "historico_analise_dfc"]:
    cursor.execute(f"SELECT id, resultado_json FROM {tabela} ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    if row:
        json_str = row[1]
        tem_acento = any(ord(c) > 127 for c in json_str)
        print(f"{tabela}: ID={row[0]}, tem acento? {'Sim' if tem_acento else 'Não'}")

conn.close()
