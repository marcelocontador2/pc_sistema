import os, re, shutil, datetime

# Arquivos onde a assinatura pode estar
arquivos = [
    "pc_frontend/panorama.html",
    "pc_backend/main.py",
    "pc_backend/app/routers/panorama.py"
]

removidos = 0

for arq in arquivos:
    if not os.path.exists(arq):
        continue
        
    # Backup
    backup = f"{arq}.bak_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(arq, backup)

    with open(arq, "r", encoding="utf-8") as f:
        conteudo = f.read()

    original = conteudo

    # 1. Se for HTML: remove a div/footer que contém "SGPC"
    if arq.endswith(".html"):
        # Remove blocos de div ou footer que tenham SGPC
        conteudo = re.sub(r'<(div|footer)[^>]*>.*?(SGPC|Documento Confidencial).*?</\1>', '', conteudo, flags=re.DOTALL | re.IGNORECASE)
        # Remove linhas soltas que tenham o texto
        conteudo = re.sub(r'^.*(SGPC|Documento Confidencial).*$\n?', '', conteudo, flags=re.MULTILINE | re.IGNORECASE)

    # 2. Se for Python: remove linhas que imprimem o texto no PDF
    elif arq.endswith(".py"):
        conteudo = re.sub(r'^.*(SGPC|Documento Confidencial).*$\n?', '', conteudo, flags=re.MULTILINE | re.IGNORECASE)

    # Se houve alteração, salva
    if conteudo != original:
        with open(arq, "w", encoding="utf-8") as f:
            f.write(conteudo)
        print(f"[OK] Rodape removido de: {arq}")
        removidos += 1
    else:
        # Se não encontrou, apaga o backup para não sujar a pasta
        os.remove(backup)

if removidos == 0:
    print("Nao encontrei o texto 'SGPC' ou 'Documento Confidencial' nos arquivos principais.")
    print("O PDF do Panorama pode estar usando uma funcao global de rodape no main.py.")
else:
    print(f"\n{removidos} arquivo(s) alterado(s).")
    print("Reinicie o servidor uvicorn (Ctrl+C e suba de novo) se ele estiver rodando.")
    print("Gere o PDF novamente para confirmar.")
