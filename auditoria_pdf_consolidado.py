import re, os

print("=" * 70)
print("AUDITORIA DE ROTAS DE PDF")
print("=" * 70)

with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

# 1. Lista todas as rotas de PDF existentes
rotas_pdf = re.findall(r'@app\.get\("(/gerar_pdf[^"]*)"\)', codigo)
print("\n[1] ROTAS /gerar_pdf_* ENCONTRADAS:")
for r in sorted(set(rotas_pdf)):
    print(f"  {r}")

# 2. Verifica a orientação padrão de cada rota (procura "orientation")
print("\n[2] ORIENTAÇÃO DE CADA ROTA (procura 'orientation=')")
for rota in sorted(set(rotas_pdf)):
    # Pega o bloco da rota
    idx = codigo.find(f'@app.get("{rota}"')
    if idx != -1:
        fim = codigo.find("\n@app.", idx + 10)
        bloco = codigo[idx:fim] if fim != -1 else codigo[idx:idx+5000]
        tem_landscape = "landscape" in bloco.lower()
        tem_portrait = "portrait" in bloco.lower() or "orientation" not in bloco.lower()
        print(f"  {rota}: {'landscape' if tem_landscape else 'portrait'}")

# 3. Verifica se usa Playwright ou FPDF
print("\n[3] MÉTODO DE GERAÇÃO (FPDF ou Playwright)")
for rota in sorted(set(rotas_pdf)):
    idx = codigo.find(f'@app.get("{rota}"')
    if idx != -1:
        fim = codigo.find("\n@app.", idx + 10)
        bloco = codigo[idx:fim] if fim != -1 else codigo[idx:idx+5000]
        tem_playwright = "sync_playwright" in bloco or "async_playwright" in bloco
        tem_fpdf = "FPDF(" in bloco
        print(f"  {rota}: {'Playwright' if tem_playwright else 'FPDF' if tem_fpdf else 'Desconhecido'}")
