c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

print("=" * 70)
print("1) ROTA /analise_dfc EXISTE?")
print("=" * 70)
if 'analise_dfc' in c:
    idx = c.find('@app.get("/analise_dfc")')
    if idx != -1:
        print("[OK] Rota @app.get('/analise_dfc') encontrada.")
    else:
        print("[ERRO] Rota @app.get('/analise_dfc') NAO encontrada.")
        # Procura qualquer coisa com analise_dfc
        for i, ln in enumerate(c.split("\n"), 1):
            if 'analise_dfc' in ln:
                print(f"  Linha {i}: {ln.strip()[:100]}")
else:
    print("[ERRO] A palavra 'analise_dfc' NAO aparece no main.py.")

print("\n" + "=" * 70)
print("2) O ROTEADOR dfc FOI INCLUIDO?")
print("=" * 70)
if 'from app.routers import dfc' in c:
    print("[OK] Import do router dfc encontrado.")
else:
    print("[ERRO] Import do router dfc NAO encontrado.")

if 'app.include_router(dfc.router)' in c:
    print("[OK] Router dfc incluido no app.")
else:
    print("[ERRO] Router dfc NAO foi incluido no app.")

print("\n" + "=" * 70)
print("3) ARQUIVO dfc.py EXISTE?")
print("=" * 70)
import os
if os.path.exists("pc_backend/app/routers/dfc.py"):
    print("[OK] pc_backend/app/routers/dfc.py existe.")
else:
    print("[ERRO] pc_backend/app/routers/dfc.py NAO existe.")
