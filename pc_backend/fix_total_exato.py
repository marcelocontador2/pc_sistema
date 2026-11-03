import shutil, datetime, ast

# Backup
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2("main.py", f"main.py.bak_{ts}")

c = open("main.py", encoding="utf-8-sig").read()

# Substitui a condição 'in' pela condição exata
antigo = 'if "CREDITO DISPON" in nome:'
novo = 'if nome == "CREDITO DISPONÍVEL" or nome == "CREDITO DISPONIVEL":'

if antigo in c:
    c = c.replace(antigo, novo)
    open("main.py", "w", encoding="utf-8").write(c)
    print("[OK] Condição de leitura do Total corrigida para bater exatamente com 'CREDITO DISPONÍVEL'!")
    ast.parse(open("main.py", encoding="utf-8").read())
    print("[OK] Sintaxe OK!")
else:
    print("[AVISO] Trecho não encontrado. Talvez já tenha sido corrigido.")
