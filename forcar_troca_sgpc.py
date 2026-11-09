import os
import shutil
from datetime import datetime

pastas = ["pc_backend", "pc_frontend"]
termos_antigos = ["SIGPC", "Sigpc", "sigpc"]
termo_novo = "SGPC"

def processar_arquivo(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()
            
        alterado = False
        for termo in termos_antigos:
            if termo in conteudo:
                conteudo = conteudo.replace(termo, termo_novo)
                alterado = True
                
        if alterado:
            shutil.copy2(caminho, caminho + ".bak_sgpc")
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(conteudo)
            print(f"  [OK] Alterado: {caminho}")
            return 1
    except Exception as e:
        # Ignora arquivos que não são texto puro (ex: imagens, executáveis)
        pass
    return 0

print("Iniciando varredura total para trocar SIGPC por SGPC...\n")
total_alterados = 0

for pasta in pastas:
    for raiz, dirs, arquivos in os.walk(pasta):
        for arq in arquivos:
            if arq.endswith((".py", ".html", ".js", ".css", ".txt", ".json")):
                caminho_completo = os.path.join(raiz, arq)
                total_alterados += processar_arquivo(caminho_completo)

print(f"\n[CONCLUIDO] Foram alterados {total_alterados} arquivos.")
