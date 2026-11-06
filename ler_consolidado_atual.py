import re

with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

# 1. Função api_relatorio_consolidado
print("=== 1. FUNÇÃO api_relatorio_consolidado ===")
idx = codigo.find("async def api_relatorio_consolidado")
if idx != -1:
    fim = codigo.find("\n@app.", idx)
    if fim == -1:
        fim = codigo.find("\ndef ", idx)
    if fim == -1:
        fim = idx + 5000
    print(codigo[idx:fim])
else:
    print("Função não encontrada.")

# 2. Rota /salvar_relatorio_consolidado
print("\n\n=== 2. ROTA salvar_relatorio_consolidado ===")
idx2 = codigo.find('@app.post("/salvar_relatorio_consolidado')
if idx2 != -1:
    fim2 = codigo.find("\n@app.", idx2 + 10)
    if fim2 == -1:
        fim2 = idx2 + 2000
    print(codigo[idx2:fim2])
else:
    print("Rota não encontrada.")

# 3. Rota /api/relatorio_consolidado (GET)
print("\n\n=== 3. ROTA api_relatorio_consolidado ===")
idx3 = codigo.find('@app.get("/api/relatorio_consolidado')
if idx3 != -1:
    fim3 = codigo.find("\n@app.", idx3 + 10)
    if fim3 == -1:
        fim3 = idx3 + 2000
    print(codigo[idx3:fim3])
else:
    print("Rota não encontrada.")
