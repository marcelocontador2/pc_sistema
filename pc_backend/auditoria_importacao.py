import ast
import os
import re

print("=== AUDITORIA DE IMPORTAÇÃO CSV ===\n")

# 1. Verificar sintaxe do main.py
try:
    with open('main.py', 'r', encoding='utf-8-sig') as f:
        codigo = f.read()
    ast.parse(codigo)
    print("[OK] Sintaxe do main.py está válida.")
except Exception as e:
    print(f"[ERRO] Sintaxe do main.py: {e}")
    exit(1)

# 2. Verificar importação do UploadFile
if "UploadFile" in codigo:
    print("[OK] UploadFile está importado.")
else:
    print("[ERRO] UploadFile NÃO está importado no main.py!")

if "from fastapi import File" in codigo or "File(" in codigo:
    print("[OK] File está importado.")
else:
    print("[ERRO] File NÃO está importado no main.py!")

# 3. Verificar se as rotas de importação existem
rotas_esperadas = [
    "/api/centro_custos/importar",
    "/analise_centro_custos",
    "/api/centro_custos/{periodo}"
]

for rota in rotas_esperadas:
    if rota in codigo:
        print(f"[OK] Rota '{rota}' encontrada.")
    else:
        print(f"[ERRO] Rota '{rota}' NÃO encontrada!")

# 4. Verificar o HTML
html_path = '../pc_frontend/analise_centro_custos.html'
if os.path.exists(html_path):
    with open(html_path, 'r', encoding='utf-8-sig') as f:
        html = f.read()
    
    if 'id="file-csv"' in html:
        print("[OK] Input de CSV encontrado no HTML.")
    else:
        print("[ERRO] Input de CSV NÃO encontrado no HTML!")
    
    if "function importarCSV" in html:
        print("[OK] Função importarCSV encontrada no HTML.")
    else:
        print("[ERRO] Função importarCSV NÃO encontrada no HTML!")
    
    if "/api/centro_custos/importar" in html:
        print("[OK] URL da API de importação está no HTML.")
    else:
        print("[ERRO] URL da API de importação NÃO está no HTML!")
else:
    print(f"[ERRO] Arquivo HTML não encontrado: {html_path}")

print("\n=== FIM DA AUDITORIA ===")
