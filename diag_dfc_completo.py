import os

c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

print("=" * 70)
print("1) ROTA /analise_dfc NO main.py")
print("=" * 70)
if '@app.get("/analise_dfc")' in c:
    print("[OK] Rota da pagina /analise_dfc existe.")
else:
    print("[ERRO] Rota da pagina /analise_dfc NAO existe.")

if '/api/analise_dfc' in c:
    print("[OK] API /api/analise_dfc existe.")
else:
    print("[ERRO] API /api/analise_dfc NAO existe.")

print("\n" + "=" * 70)
print("2) ROTEADOR dfc.py")
print("=" * 70)
if os.path.exists("pc_backend/app/routers/dfc.py"):
    print("[OK] Arquivo dfc.py existe.")
else:
    print("[ERRO] Arquivo dfc.py NAO existe.")

if 'from app.routers import dfc' in c:
    print("[OK] Import do router dfc existe.")
else:
    print("[ERRO] Import do router dfc NAO existe.")

if 'app.include_router(dfc.router)' in c:
    print("[OK] Router dfc incluido.")
else:
    print("[ERRO] Router dfc NAO incluido.")

print("\n" + "=" * 70)
print("3) HISTORICO E PDF DA DFC")
print("=" * 70)
for rota in ['/historico_analise_dfc', '/salvar_analise_dfc', '/gerar_pdf_analise_dfc', '/excluir_analise_dfc']:
    if rota in c:
        print(f"[OK] Rota {rota} existe.")
    else:
        print(f"[ERRO] Rota {rota} NAO existe.")

print("\n" + "=" * 70)
print("4) ARQUIVO analise_dfc.html")
print("=" * 70)
if os.path.exists("pc_frontend/analise_dfc.html"):
    print("[OK] analise_dfc.html existe.")
else:
    print("[ERRO] analise_dfc.html NAO existe.")
