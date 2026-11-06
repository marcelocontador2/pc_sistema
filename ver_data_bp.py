import os, datetime

caminho = r"pc_storage/uploads_raw/BALANCO_PATRIMONIAL_2026_TRIMESTRE_3.csv"
if os.path.exists(caminho):
    data_mod = datetime.datetime.fromtimestamp(os.path.getmtime(caminho)).strftime("%d/%m/%Y %H:%M")
    print(f"Arquivo: {caminho}")
    print(f"Modificado em: {data_mod}")
    print("(Se a data for de hoje, o upload funcionou!)")
else:
    print("[ERRO] Arquivo nao encontrado.")
