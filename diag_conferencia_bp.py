import requests, json

# Testar a API de conferencia
url = "http://127.0.0.1:9994/api/conferencia/2026-TRIMESTRE-3"
try:
    response = requests.get(url, timeout=10)
    print("=" * 70)
    print("1) API DE CONFERENCIA (status:", response.status_code, ")")
    print("=" * 70)
    data = response.json()
    for analise in data.get("analises", []):
        if "Balanço Patrimonial" in analise.get("titulo", ""):
            print(json.dumps(analise, indent=2, ensure_ascii=False))
            break
except Exception as e:
    print("Erro:", e)

# Verificar o CSV na parte do Passivo
print("\n" + "=" * 70)
print("2) ESTRUTURA DO CSV (linhas do Passivo)")
print("=" * 70)
import csv, os
caminho = r"pc_storage/uploads_raw/BALANCO_PATRIMONIAL_2026_TRIMESTRE_3.csv"
if os.path.exists(caminho):
    with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
        leitor = csv.reader(f, delimiter=";")
        for i, row in enumerate(leitor):
            if i >= 50:
                break
            # Mostra linhas que tem "PASSIVO" ou "PATRIMONIO" ou "TOTAL"
            linha_str = ";".join(row).upper()
            if "PASSIVO" in linha_str or "PATRIM" in linha_str or "TOTAL" in linha_str:
                colunas = [f"Col{j}={repr(c.strip()[:40])}" for j, c in enumerate(row) if c.strip()]
                if colunas:
                    print(f"Linha {i+1}: " + " | ".join(colunas))
else:
    print("[ERRO] CSV nao encontrado.")
