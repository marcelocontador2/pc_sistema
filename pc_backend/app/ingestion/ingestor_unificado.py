import psycopg2
import hashlib
import os
import csv
import re

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "pc_database",
    "user": "postgres",
    "password": "pc_admin_2026"
}

def limpar_valor(valor):
    if valor is None or str(valor).strip() == "":
        return 0.0
    v = str(valor).strip().upper()
    if v.endswith("D") or v.endswith("C"):
        v = v[:-1]
    v = v.replace("R$", "").replace(".", "").replace(",", ".")
    try:
        return float(v)
    except:
        return 0.0

def normalizar(texto):
    return re.sub(r'\s+', ' ', str(texto).strip().upper())

def get_periodo_id(cursor, ano, periodo_acumulado):
    cursor.execute("SELECT id FROM periodo WHERE ano = %s AND periodo_acumulado = %s;", (ano, periodo_acumulado))
    res = cursor.fetchone()
    return res[0] if res else None

def inserir_documento(cursor, periodo_id, tipo, nome_arquivo, hash_arquivo):
    cursor.execute("""
        INSERT INTO documento_importado (periodo_id, tipo, nome_arquivo, file_hash, status_processamento)
        VALUES (%s, %s, %s, %s, 'PROCESSADO') RETURNING id;
    """, (periodo_id, tipo, nome_arquivo, hash_arquivo))
    return cursor.fetchone()[0]

def inserir_valor(cursor, doc_id, periodo_id, grupo, valor):
    if valor != 0.0:
        cursor.execute("""
            INSERT INTO demonstracao_resumo (documento_id, periodo_id, grupo_demonstrativo, valor_atual)
            VALUES (%s, %s, %s, %s);
        """, (doc_id, periodo_id, grupo, valor))

def ler_linhas(caminho_csv):
    try:
        with open(caminho_csv, "r", encoding="utf-8") as f:
            return list(csv.reader(f, delimiter=";"))
    except UnicodeDecodeError:
        with open(caminho_csv, "r", encoding="latin-1") as f:
            return list(csv.reader(f, delimiter=";"))

def processar_bp_comparativo(caminho_csv):
    """Processa o BP comparativo (com 2026 e 2025)."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    with open(caminho_csv, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    pid_2026 = get_periodo_id(cursor, 2026, "Jan-Set")
    pid_2025 = get_periodo_id(cursor, 2025, "Jan-Set")

    doc_2026 = inserir_documento(cursor, pid_2026, "BALANCO_PATRIMONIAL", os.path.basename(caminho_csv), file_hash)
    doc_2025 = inserir_documento(cursor, pid_2025, "BALANCO_PATRIMONIAL", os.path.basename(caminho_csv), file_hash)

    linhas = ler_linhas(caminho_csv)
    mapa = {
        "ATIVO CIRCULANTE": "Ativo Circulante",
        "ATIVO NÃƒO CIRCULANTE": "Ativo Nao Circulante",
        "PASSIVO CIRCULANTE": "Passivo Circulante",
        "PASSIVO NAO-CIRCULANTE": "Passivo Nao Circulante",
        "TOTAL DO PATRIMÃ”NIO LÃQUIDO": "Patrimonio Liquido",
        "TOTAL": "Total Geral"
    }
    for row in linhas[6:]:
        # Ativo (2026 na coluna 1, 2025 na coluna 2)
        if len(row) >= 3:
            d = normalizar(row[0])
            v2026 = limpar_valor(row[1]) if len(row) > 1 else 0.0
            v2025 = limpar_valor(row[2]) if len(row) > 2 else 0.0
            if d in mapa:
                if v2026 != 0.0: inserir_valor(cursor, doc_2026, pid_2026, mapa[d], v2026)
                if v2025 != 0.0: inserir_valor(cursor, doc_2025, pid_2025, mapa[d], v2025)

        # Passivo (2026 na coluna 4, 2025 na coluna 5)
        if len(row) >= 6:
            d = normalizar(row[3])
            v2026 = limpar_valor(row[4]) if len(row) > 4 else 0.0
            v2025 = limpar_valor(row[5]) if len(row) > 5 else 0.0
            if d in mapa:
                if v2026 != 0.0: inserir_valor(cursor, doc_2026, pid_2026, mapa[d], v2026)
                if v2025 != 0.0: inserir_valor(cursor, doc_2025, pid_2025, mapa[d], v2025)

    conn.commit(); cursor.close(); conn.close()
    print(f"BP Comparativo processado (2026 e 2025): {os.path.basename(caminho_csv)}")

def processar_bo(caminho_csv, ano, periodo_acumulado):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    periodo_id = get_periodo_id(cursor, ano, periodo_acumulado)
    if not periodo_id:
        print(f"PerÃ­odo {ano}/{periodo_acumulado} nÃ£o encontrado. Pulando {os.path.basename(caminho_csv)}")
        return
    with open(caminho_csv, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    doc_id = inserir_documento(cursor, periodo_id, "BALANCO_ORCAMENTARIO", os.path.basename(caminho_csv), file_hash)
    linhas = ler_linhas(caminho_csv)
    linhas_norm = [[normalizar(c) for c in row] for row in linhas]
    idx_rec, idx_desp = None, None
    for row in linhas_norm:
        for i, c in enumerate(row):
            if "RECEITAS REALIZADAS" in c: idx_rec = i
            if "DESPESAS EMPENHADAS" in c: idx_desp = i
        if idx_rec is not None and idx_desp is not None: break
    for row in linhas:
        texto = ";".join([normalizar(c) for c in row])
        if "SUB-TOTAL DAS RECEITAS" in texto and idx_rec is not None and len(row) > idx_rec:
            inserir_valor(cursor, doc_id, periodo_id, "Receita Realizada", limpar_valor(row[idx_rec]))
        if "SUB-TOTAL DAS DESPESAS" in texto and idx_desp is not None and len(row) > idx_desp:
            inserir_valor(cursor, doc_id, periodo_id, "Despesa Empenhada", limpar_valor(row[idx_desp]))
    conn.commit(); cursor.close(); conn.close()
    print(f"BO processado ({ano}/{periodo_acumulado}): {os.path.basename(caminho_csv)}")

def processar_bf_comparativo(caminho_csv):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    with open(caminho_csv, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    pid_2026 = get_periodo_id(cursor, 2026, "Jan-Set")
    pid_2025 = get_periodo_id(cursor, 2025, "Jan-Set")

    doc_2026 = inserir_documento(cursor, pid_2026, "BALANCO_FINANCEIRO", os.path.basename(caminho_csv), file_hash)
    doc_2025 = inserir_documento(cursor, pid_2025, "BALANCO_FINANCEIRO", os.path.basename(caminho_csv), file_hash)

    linhas = ler_linhas(caminho_csv)
    mapa = {
        "RECEITA ORÃ‡AMENTÃRIA": "Receita Orcamentaria",
        "DESPESA ORÃ‡AMENTÃRIA": "Despesa Orcamentaria",
        "SALDO EM ESPÃ‰CIE DO EXERCÃCIO ANTERIOR": "Saldo Inicial",
        "SALDO EM ESPÃ‰CIE PARA O EXERCÃCIO SEGUINTE": "Saldo Final"
    }
    for row in linhas:
        if len(row) >= 3:
            d = normalizar(row[0])
            v2026 = limpar_valor(row[1])
            v2025 = limpar_valor(row[2])
            if d in mapa:
                if v2026 != 0.0: inserir_valor(cursor, doc_2026, pid_2026, mapa[d], v2026)
                if v2025 != 0.0: inserir_valor(cursor, doc_2025, pid_2025, mapa[d], v2025)

    conn.commit(); cursor.close(); conn.close()
    print(f"BF Comparativo processado (2026 e 2025): {os.path.basename(caminho_csv)}")

def processar_dfc_comparativo(caminho_csv):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    with open(caminho_csv, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    pid_2026 = get_periodo_id(cursor, 2026, "Jan-Set")
    pid_2025 = get_periodo_id(cursor, 2025, "Jan-Set")

    doc_2026 = inserir_documento(cursor, pid_2026, "DFC", os.path.basename(caminho_csv), file_hash)
    doc_2025 = inserir_documento(cursor, pid_2025, "DFC", os.path.basename(caminho_csv), file_hash)

    linhas = ler_linhas(caminho_csv)
    mapa = {
        "CAIXA E EQUIVALENTES DE CAIXA INICIAL": "Caixa Inicial",
        "CAIXA E EQUIVALENTES DE CAIXA FINAL": "Caixa Final",
        "GERAÃ‡ÃƒO LÃQUIDA DE CAIXA E EQUIVALENTES DE CAIXA": "Geracao Liquida Caixa"
    }
    for row in linhas:
        if len(row) >= 4:
            d = normalizar(row[0])
            v2026 = limpar_valor(row[3]) if len(row) > 3 else 0.0
            v2025 = limpar_valor(row[4]) if len(row) > 4 else 0.0
            if d in mapa:
                if v2026 != 0.0: inserir_valor(cursor, doc_2026, pid_2026, mapa[d], v2026)
                if v2025 != 0.0: inserir_valor(cursor, doc_2025, pid_2025, mapa[d], v2025)

    conn.commit(); cursor.close(); conn.close()
    print(f"DFC Comparativo processado (2026 e 2025): {os.path.basename(caminho_csv)}")

def processar_dvp_comparativo(caminho_csv):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    with open(caminho_csv, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    pid_2026 = get_periodo_id(cursor, 2026, "Jan-Set")
    pid_2025 = get_periodo_id(cursor, 2025, "Jan-Set")

    doc_2026 = inserir_documento(cursor, pid_2026, "DVP", os.path.basename(caminho_csv), file_hash)
    doc_2025 = inserir_documento(cursor, pid_2025, "DVP", os.path.basename(caminho_csv), file_hash)

    linhas = ler_linhas(caminho_csv)
    for row in linhas:
        if len(row) >= 7:
            texto_linha = ";".join([normalizar(c) for c in row])
            if "VARIAÃ‡ÃƒO PATRIMONIAL AUMENTATIVA" in texto_linha and "TOTAL" not in texto_linha:
                v2026 = limpar_valor(row[2]) if len(row) > 2 else 0.0
                v2025 = limpar_valor(row[3]) if len(row) > 3 else 0.0
                if v2026 != 0.0: inserir_valor(cursor, doc_2026, pid_2026, "Variacoes Ativas", v2026)
                if v2025 != 0.0: inserir_valor(cursor, doc_2025, pid_2025, "Variacoes Ativas", v2025)
            if "VARIAÃ‡ÃƒO PATRIMONIAL DIMINUTIVA" in texto_linha and "TOTAL" not in texto_linha:
                v2026 = limpar_valor(row[6]) if len(row) > 6 else 0.0
                v2025 = limpar_valor(row[7]) if len(row) > 7 else 0.0
                if v2026 != 0.0: inserir_valor(cursor, doc_2026, pid_2026, "Variacoes Diminutivas", v2026)
                if v2025 != 0.0: inserir_valor(cursor, doc_2025, pid_2025, "Variacoes Diminutivas", v2025)
            if "SUPERÃVIT DO EXERCÃCIO" in texto_linha:
                v2026 = limpar_valor(row[6]) if len(row) > 6 else 0.0
                v2025 = limpar_valor(row[7]) if len(row) > 7 else 0.0
                if v2026 != 0.0: inserir_valor(cursor, doc_2026, pid_2026, "Superavit Patrimonial", v2026)
                if v2025 != 0.0: inserir_valor(cursor, doc_2025, pid_2025, "Superavit Patrimonial", v2025)

    conn.commit(); cursor.close(); conn.close()
    print(f"DVP Comparativo processado (2026 e 2025): {os.path.basename(caminho_csv)}")

def processar_dmpl(caminho_csv, ano):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    periodo_id = get_periodo_id(cursor, ano, "Jan-Set")
    if not periodo_id:
        print(f"PerÃ­odo {ano} nÃ£o encontrado. Pulando {os.path.basename(caminho_csv)}")
        return
    with open(caminho_csv, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    doc_id = inserir_documento(cursor, periodo_id, "DMPL", os.path.basename(caminho_csv), file_hash)
    linhas = ler_linhas(caminho_csv)
    
    for row in linhas:
        if len(row) >= 8:
            d = normalizar(row[0])
            if d == "SALDOS INICIAIS":
                inserir_valor(cursor, doc_id, periodo_id, "PL Inicial", abs(limpar_valor(row[7])))
            elif d == "RESULTADO DO PERÃODO":
                inserir_valor(cursor, doc_id, periodo_id, "Resultado Periodo", abs(limpar_valor(row[7])))
            elif d == "SALDOS FINAIS":
                inserir_valor(cursor, doc_id, periodo_id, "PL Final", abs(limpar_valor(row[7])))
    conn.commit(); cursor.close(); conn.close()
    print(f"DMPL processado ({ano}): {os.path.basename(caminho_csv)}")

if __name__ == "__main__":
    pasta = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_storage\uploads_raw"
    for arquivo in os.listdir(pasta):
        caminho = os.path.join(pasta, arquivo)
        nome = arquivo.lower()
        
        ano = 2026
        if "2025" in nome:
            ano = 2025
        
        periodo_acumulado = "Jan-Set"
        if "out" in nome.lower() or "dez" in nome.lower() or "out-dez" in nome.lower():
            periodo_acumulado = "Out-Dez"
        
        # Prioridade: comparativo tem os dois anos
        if "comparativo" in nome and nome.startswith("balancopatrimonial"):
            processar_bp_comparativo(caminho)
        elif nome.startswith("balancopatrimonial"):
            processar_bp_comparativo(caminho)  # O BP normal tambÃ©m pode ser comparativo
        elif nome.startswith("balancoorcamentario"):
            processar_bo(caminho, ano, periodo_acumulado)
        elif nome.startswith("balancofinanceiro"):
            processar_bf_comparativo(caminho)
        elif nome.startswith("dfc"):
            processar_dfc_comparativo(caminho)
        elif nome.startswith("variacoes"):
            processar_dvp_comparativo(caminho)
        elif nome.startswith("dmpl"):
            processar_dmpl(caminho, ano)
