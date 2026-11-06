import csv, json, sqlite3, os

# Encoding correto: os CSVs foram salvos em UTF-8 originalmente
ENCODING = "utf-8"

db_path = os.path.join("pc_storage", "banco_dados.db")
pasta_uploads = os.path.join("pc_storage", "uploads_raw")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# =========================================================
# 1. Corrigir o DFC
# =========================================================
csv_dfc = os.path.join(pasta_uploads, "DFC_2026_TRIMESTRE_3.csv")
if os.path.exists(csv_dfc):
    print(f"[DFC] Lendo {csv_dfc} em {ENCODING}")
    
    # Verifica se o arquivo realmente é UTF-8 lendo os bytes
    with open(csv_dfc, "rb") as f:
        raw = f.read(500)
    
    # Tenta detectar encoding
    for enc in ["utf-8", "latin-1", "cp1252"]:
        try:
            raw.decode(enc)
            print(f"  [INFO] Arquivo pode ser lido em {enc}")
            break
        except:
            pass
    
    # Lê o CSV e re-salva o JSON com acentos corretos
    with open(csv_dfc, "r", encoding=ENCODING, errors="replace") as f:
        linhas = list(csv.reader(f, delimiter=";"))
    
    # Mostra os primeiros campos para validar
    print(f"  Primeiras 5 linhas (2 primeiros campos):")
    for i, linha in enumerate(linhas[:5]):
        print(f"    Linha {i+1}: {linha[:2]}")
    
    # Reconstrói o JSON a partir do CSV (mesmo formato do banco)
    dados_corrigidos = {
        "erro": False,
        "dados": {
            "operacional": {"ingressos": {}, "desembolsos": {}, "liquido": {}},
            "investimento": {"ingressos": {}, "desembolsos": {}, "liquido": {}},
            "financiamento": {"ingressos": {}, "desembolsos": {}, "liquido": {}},
            "caixa": {"inicial": {}, "final": {}, "geracao": {}},
            "textos": []  # guarda os textos com acentos
        }
    }
    
    # Extrai apenas os textos do CSV (com acentos) para o banco
    for linha in linhas:
        if linha and linha[0].strip():
            dados_corrigidos["dados"]["textos"].append(linha[0].strip())
    
    # Atualiza o último registro do DFC
    cursor.execute("SELECT id FROM historico_analise_dfc ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    if row:
        id_dfc = row[0]
        cursor.execute(
            "UPDATE historico_analise_dfc SET resultado_json = ? WHERE id = ?",
            (json.dumps(dados_corrigidos, ensure_ascii=False), id_dfc)
        )
        print(f"  [OK] DFC id={id_dfc} atualizado com textos corretos.")
else:
    print("[AVISO] CSV do DFC não encontrado.")

# =========================================================
# 2. Corrigir o BF
# =========================================================
csv_bf = os.path.join(pasta_uploads, "BALANCO_FINANCEIRO_2026_TRIMESTRE_3.csv")
if os.path.exists(csv_bf):
    print(f"\n[BF] Lendo {csv_bf} em {ENCODING}")
    
    with open(csv_bf, "r", encoding=ENCODING, errors="replace") as f:
        linhas = list(csv.reader(f, delimiter=";"))
    
    print(f"  Primeiras 5 linhas (2 primeiros campos):")
    for i, linha in enumerate(linhas[:5]):
        print(f"    Linha {i+1}: {linha[:2]}")
    
    dados_corrigidos_bf = {
        "erro": False,
        "dados": {
            "textos": []
        }
    }
    for linha in linhas:
        if linha and linha[0].strip():
            dados_corrigidos_bf["dados"]["textos"].append(linha[0].strip())
    
    cursor.execute("SELECT id FROM historico_analise_financeira_bf ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    if row:
        id_bf = row[0]
        cursor.execute(
            "UPDATE historico_analise_financeira_bf SET resultado_json = ? WHERE id = ?",
            (json.dumps(dados_corrigidos_bf, ensure_ascii=False), id_bf)
        )
        print(f"  [OK] BF id={id_bf} atualizado com textos corretos.")
else:
    print("[AVISO] CSV do BF não encontrado.")

conn.commit()
conn.close()
print("\n[OK] Banco atualizado com acentuação correta.")
