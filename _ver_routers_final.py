with open("pc_backend/main.py", "r", encoding="utf-8") as f:
    linhas = f.readlines()

print("=== include_router no main.py (todos) ===")
for i, linha in enumerate(linhas, 1):
    if "include_router" in linha and not linha.strip().startswith("#"):
        print(f"{i:>5}: {linha.strip()}")

print()
print("=== Total de rotas ativas no main.py ===")
import re
count = 0
for linha in linhas:
    if re.match(r'\s*@app\.(get|post|put|delete)', linha):
        count += 1
print(f"  {count} rotas ativas")

print()
print("=== Rotas comentadas restantes (se houver) ===")
comentadas = 0
for linha in linhas:
    if linha.strip().startswith("# @app.") or linha.strip().startswith("#@app."):
        comentadas += 1
print(f"  {comentadas} rotas comentadas")

print()
print("=== Comentarios [REMOVIDO restantes ===")
removidos = 0
for linha in linhas:
    if "[REMOVIDO" in linha:
        removidos += 1
print(f"  {removidos} comentarios [REMOVIDO")
