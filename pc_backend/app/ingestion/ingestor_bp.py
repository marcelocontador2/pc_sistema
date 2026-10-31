import psycopg2
import hashlib
import os
import pandas as pd
DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "pc_database",
    "user": "postgres",
    "password": "pc_admin_2026"
}
def limpar_valor(valor_str):
    if pd.isna(valor_str) or str(valor_str).strip() == "":
        return 0.0
    v = str(valor_str).strip().upper()
    if v.endswith("D") or v.endswith("C"):
        v = v[:-1]
    v = v.replace("R$", "").replace(".", "").replace(",", ".")
    try:
        return float(v)
    except ValueError:
        return 0.0
def inserir_bp(caminho_csv):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM periodo WHERE ano = 2026 AND periodo_acumulado = 'Jan-Set';")
    periodo_id = cursor.fetchone()[0]
    with open(caminho_csv, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    cursor.execute("""
        INSERT INTO documento_importado (periodo_id, tipo, nome_arquivo, file_hash, status_processamento)
        VALUES (%s, %s, %s, %s, 'PROCESSADO') RETURNING id;
    """, (periodo_id, "BALANCO_PATRIMONIAL", os.path.basename(caminho_csv), file_hash))
    documento_id = cursor.fetchone()[0]
    # Lê o CSV forçando UTF-8
    df = pd.read_csv(caminho_csv, sep=";", encoding="utf-8")
    print("Colunas encontradas:", df.columns.tolist())
    print("Primeiras linhas:")
    print(df.head())
    df.columns = [c.strip().lower() for c in df.columns]
    inseridos = 0
    for _, row in df.iterrows():
        grupo = str(row.get("conta", "")).strip()
        if not grupo:
            continue
        valor_2026 = limpar_valor(row.get("valor_2026", 0))
        valor_2025 = limpar_valor(row.get("valor_2025", 0))
        cursor.execute("""
            INSERT INTO demonstracao_resumo (documento_id, periodo_id, grupo_demonstrativo, valor_atual)
            VALUES (%s, %s, %s, %s);
        """, (documento_id, periodo_id, grupo, valor_2026))
        inseridos += 1
        if valor_2025 != 0.0:
            cursor.execute("""
                INSERT INTO demonstracao_resumo (documento_id, periodo_id, grupo_demonstrativo, valor_atual)
                VALUES (%s, %s, %s, %s);
            """, (documento_id, periodo_id, f"{grupo}_2025", valor_2025))
            inseridos += 1
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Ingestão do Balanço Patrimonial concluída! {inseridos} linhas gravadas no banco.")
if __name__ == "__main__":
    arquivo = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_storage\uploads_raw\Balanco_Patrimonial.csv"
    if os.path.exists(arquivo):
        inserir_bp(arquivo)
    else:
        print(f"Arquivo não encontrado: {arquivo}")
