import requests

url = "http://127.0.0.1:9994/upload"

# Caminho do arquivo que voce vai enviar (ajuste se o nome for diferente)
caminho_arquivo = r"pc_storage/uploads_raw/BALANCO_PATRIMONIAL_2026_TRIMESTRE_3.csv"

# Se o arquivo nao existir, tenta encontrar outro
import os, glob
if not os.path.exists(caminho_arquivo):
    # Procura qualquer arquivo de BP na pasta
    candidatos = glob.glob(r"pc_storage/uploads_raw/BALANCO_PATRIMONIAL_*.csv")
    if candidatos:
        caminho_arquivo = candidatos[0]
    else:
        print("[ERRO] Nenhum arquivo de BP encontrado. Use um arquivo de teste.")
        caminho_arquivo = None

if caminho_arquivo and os.path.exists(caminho_arquivo):
    print(f"Enviando arquivo: {caminho_arquivo}")
    with open(caminho_arquivo, "rb") as f:
        files = {"file": (os.path.basename(caminho_arquivo), f, "text/csv")}
        data = {
            "tipo_relatorio": "BALANCO_PATRIMONIAL",
            "ano": "2026",
            "periodo_tipo": "TRIMESTRE",
            "periodo_valor": "3"
        }
        try:
            response = requests.post(url, files=files, data=data, timeout=30)
            print("Status:", response.status_code)
            print("Resposta:", response.text)
        except Exception as e:
            print("Erro ao enviar:", e)
else:
    print("[ERRO] Arquivo nao encontrado para teste.")
