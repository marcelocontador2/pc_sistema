import ast, os

back_path = r"pc_backend\main.py"
try:
    c = open(back_path, encoding="utf-8-sig").read()
    ast.parse(c)
    print("[OK] Sintaxe do main.py esta correta.")
    
    # Verifica se a API do BP existe
    if "/api/analise_bp" in c:
        print("[OK] A rota /api/analise_bp existe no main.py.")
    else:
        print("[ERRO] A rota /api/analise_bp NAO existe no main.py.")
        
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada no main.py: {e}")
    print("Linha do erro:", e.lineno)
