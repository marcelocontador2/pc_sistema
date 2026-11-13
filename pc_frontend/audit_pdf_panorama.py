import re

with open("panorama.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. BOTAO GERAR PDF ===")
btn = re.search(r'<button[^>]*>([^<]*Gerar PDF[^<]*)</button>', s)
if btn:
    print(btn.group(0))
else:
    print("Botao 'Gerar PDF' nao encontrado.")

print("\n=== 2. FUNCAO gerarPDF() (se existir) ===")
match = re.search(r'function\s+(gerarPDF|gerarPDFHistorico)\s*\([^)]*\)\s*\{.*?\n\}', s, re.DOTALL)
if match:
    print(match.group(0)[:1000])
else:
    print("Funcao gerarPDF() nao encontrada.")

print("\n=== 3. ROTA DE PDF NO BACKEND ===")
with open("../pc_backend/main.py", "r", encoding="utf-8") as f:
    main = f.read()
rotas = re.findall(r'@app\.(?:get|post)\("(/gerar_pdf_panorama[^"]*)"\)', main)
if rotas:
    for r in rotas:
        print(f"  - {r}")
else:
    print("Nenhuma rota de PDF do panorama encontrada no main.py.")
