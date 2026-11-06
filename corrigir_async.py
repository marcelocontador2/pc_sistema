import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/index.html"
shutil.copy2(arq, f"{arq}.bak_async_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Adiciona "async" na declaracao da funcao enviarArquivo
antigo = "function enviarArquivo(event) {"
novo = "async function enviarArquivo(event) {"

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] Funcao enviarArquivo agora e async (o await do fetch vai funcionar).")
else:
    print("[AVISO] Trecho nao encontrado. Verifique se a funcao ja e async.")
