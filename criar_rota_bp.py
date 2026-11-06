import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_rota_bp_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Verifica se a rota ja existe
if 'async def serve_analise_bp' in c:
    print("[AVISO] A rota /analise_bp ja existe no main.py.")
else:
    # Procura a rota /analise_dfc (que ja existe) para inserir a /analise_bp antes ou depois
    idx = c.find('@app.get("/analise_dfc")')
    if idx == -1:
        idx = c.find("if __name__")
    if idx == -1:
        idx = len(c)
    
    rota_bp = '''
@app.get("/analise_bp")
async def serve_analise_bp():
    from fastapi.responses import FileResponse
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_bp.html")
    return FileResponse(caminho, headers={"Cache-Control": "no-store, no-cache, must-revalidate"})

'''
    
    c = c[:idx] + rota_bp + c[idx:]
    open(back_path, "w", encoding="utf-8").write(c)
    
    try:
        ast.parse(open(back_path, encoding="utf-8").read())
        print("[OK] Rota /analise_bp criada no main.py e sintaxe validada.")
    except SyntaxError as e:
        print(f"[ERRO] Sintaxe quebrada: {e}")
        shutil.copy2(f"{back_path}.bak_rota_bp_{ts}", back_path)
        print("[OK] Backup restaurado.")
