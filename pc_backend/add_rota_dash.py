import shutil, ast, datetime

shutil.copy2("main.py", f"main.py.bak_dash_{datetime.datetime.now().strftime('%H%M%S')}")
c = open("main.py", encoding="utf-8-sig").read()

# Verifica se a rota já existe para não duplicar
if '@app.get("/dashboard_despesas")' not in c:
    nova_rota = '''
@app.get("/dashboard_despesas")
def get_dashboard_despesas():
    from fastapi.responses import FileResponse
    import os
    caminho = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pc_frontend", "dashboard_despesas.html")
    return FileResponse(caminho)

'''
    # Insere a nova rota logo antes da rota do comparativo de despesas
    ancora = '@app.get("/analise_comparativo_despesas")'
    if ancora in c:
        c = c.replace(ancora, nova_rota + ancora, 1)
        open("main.py", "w", encoding="utf-8").write(c)
        ast.parse(open("main.py", encoding="utf-8").read())
        print("[OK] Rota /dashboard_despesas adicionada com sucesso e Sintaxe OK!")
    else:
        print("[AVISO] Não achei a âncora, mas a rota não existe.")
else:
    print("[AVISO] A rota já existe no sistema.")
