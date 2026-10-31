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
def limpar(valor):
    if pd.isna(valor) or str(valor).strip() == "": return 0.0, None
    v = str(valor).strip().upper()
    nat = None
    if v.endswith("D"): nat, v = "D", v[:-1]
    elif v.endswith("C"): nat, v = "C", v[:-1]
    v = v.replace("R$", "").replace(".", "").replace(",", ".")
    try: return float(v), nat
    except: return 0.0, None
def inserir_balancete(caminho_csv):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    # Busca o periodo_id (Jan-Set/2026)
    cursor.execute("SELECT id FROM periodo WHERE ano = 2026 AND periodo_acumulado = 'Jan-Set';")
    periodo_id = cursor.fetchone()[0]
    # Calcula o hash do arquivo
    with open(caminho_csv, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    # Insere o documento
    cursor.execute("""
        INSERT INTO documento_importado (periodo_id, tipo, nome_arquivo, file_hash, status_processamento)
        VALUES (%s, %s, %s, %s, 'PROCESSADO') RETURNING id;
    """, (periodo_id, "BALANCETE", os.path.basename(caminho_csv), file_hash))
    documento_id = cursor.fetchone()[0]
    # Lê o CSV com fallback de encoding
    try:
        df = pd.read_csv(caminho_csv, sep=";", skiprows=6, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(caminho_csv, sep=";", skiprows=6, encoding="latin-1")
    df.columns = ["codigo_conta", "descricao_conta", "saldo_anterior", "debito", "credito", "saldo_atual"]
    df = df[df["codigo_conta"].notna()]
    df = df[df["codigo_conta"].astype(str).str[0].str.isdigit()]
    inseridos = 0
    for _, row in df.iterrows():
        sa, _ = limpar(row["saldo_anterior"])
        db, _ = limpar(row["debito"])
        cr, _ = limpar(row["credito"])
        sat, nat = limpar(row["saldo_atual"])
        partes = str(row["codigo_conta"]).split(" - ", 1)
        codigo = partes[0].strip()
        descricao = partes[1].strip() if len(partes) > 1 else ""
        cursor.execute("""
            INSERT INTO balancete_linha (documento_id, codigo_conta, descricao_conta, saldo_anterior, debito, credito, saldo_atual, natureza_saldo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """, (documento_id, codigo, descricao, sa, db, cr, sat, nat))
        inseridos += 1
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Ingestão concluída! {inseridos} linhas gravadas no banco (documento_id: {documento_id}).")
if __name__ == "__main__":
    arquivo = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_storage\uploads_raw\Balancete.csv"
    if os.path.exists(arquivo):
        inserir_balancete(arquivo)
    else:
        print(f"Arquivo não encontrado: {arquivo}")
