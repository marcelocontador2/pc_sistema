import os

print("=== 1. PROCURANDO 'Análises Contábeis' EM TODOS OS ARQUIVOS ===")
for root, dirs, files in os.walk("."):
    # Pula pastas de backup, venv e git
    dirs[:] = [d for d in dirs if d not in ("pc_venv", "__pycache__", ".git", "_backups_arquivo", "_arquivo_20261031", "node_modules")]
    
    for nome in files:
        if not (nome.endswith(".html") or nome.endswith(".py")):
            continue
            
        caminho = os.path.join(root, nome)
        try:
            with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
        except Exception:
            continue
            
        if "Análises Contábeis" in txt or "Analises Contabeis" in txt:
            print(f"\n>>> Encontrado em: {caminho}")
            idx = txt.find("Análises Contábeis")
            if idx == -1:
                idx = txt.find("Analises Contabeis")
            
            # Mostra o contexto de 400 caracteres antes e depois
            contexto = txt[max(0, idx-400):idx+600]
            print("..." + contexto + "...")

print("\n=== 2. PROCURANDO ROTAS DE MENU NO main.py ===")
arq_main = r"pc_backend\main.py"
if os.path.exists(arq_main):
    with open(arq_main, "r", encoding="utf-8") as f:
        main_code = f.read()
    
    # Procura por "Análise" no main.py
    for linha in main_code.split("\n"):
        if "Análise" in linha or "Analise" in linha:
            if "href" in linha.lower() or "menu" in linha.lower() or "<li" in linha:
                print("main.py >", linha.strip()[:150])
else:
    print("main.py não encontrado.")

print("\n=== 3. LISTANDO OS 10 MAIORES HTMLs DA PASTA FRONTEND ===")
arquivos = []
for nome in os.listdir("pc_frontend"):
    if nome.endswith(".html"):
        caminho = os.path.join("pc_frontend", nome)
        tamanho = os.path.getsize(caminho)
        arquivos.append((tamanho, nome))

for tam, nome in sorted(arquivos, reverse=True)[:10]:
    print(f"{tam:>8} bytes - {nome}")
