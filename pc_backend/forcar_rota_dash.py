import shutil, ast, datetime

shutil.copy2("main.py", f"main.py.bak_rota_dash_{datetime.datetime.now().strftime('%H%M%S')}")
c = open("main.py", encoding="utf-8-sig").read()

# Verifica se a rota já existe
if "def get_dashboard_despesas():" in c:
    print("[AVISO] A função já existe no arquivo. Removendo versão antiga para recriar...")
    import re
    c = re.sub(r'@app\.get\("/dashboard_despesas"\)\s*def get_dashboard_despesas\(\):.*?return FileResponse\([^\)]+\)', '', c, flags=re.DOTALL)

# Nova rota infalível
nova_rota = '''
@app.get("/dashboard_despesas")
def get_dashboard_despesas():
    from fastapi.responses import FileResponse
    import os
    caminho = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pc_frontend", "dashboard_despesas.html")
    if os.path.exists(caminho):
        return FileResponse(caminho)
    return {"erro": True, "mensagem": "Arquivo dashboard_despesas.html nao encontrado"}

'''

# Insere logo no início do arquivo (após as importações), para garantir que o FastAPI leia
if '@app.get("/dashboard_despesas")' not in c:
    # Encontra a primeira ocorrência de @app.get ou @app.post
    import re
    match = re.search(r'@app\.(get|post|put|delete)\(', c)
    if match:
        idx = match.start()
        c = c[:idx] + nova_rota + c[idx:]
        open("main.py", "w", encoding="utf-8").write(c)
        ast.parse(open("main.py", encoding="utf-8").read())
        print("[OK] Rota /dashboard_despesas inserida no topo e Sintaxe OK!")
    else:
        print("[ERRO] Não foi possível encontrar onde inserir a rota.")
else:
    print("[AVISO] A rota já estava no arquivo, mas o servidor não a leu.")
    open("main.py", "w", encoding="utf-8").write(c)
