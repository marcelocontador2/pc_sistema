c = open("pc_frontend/analise_bp.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("1) QUAL ROTA O BOTAO 'GERAR PDF' CHAMA?")
print("=" * 70)
# Procura a funcao gerarPDF
idx = c.find("function gerarPDF")
if idx != -1:
    fim = c.find("}", idx) + 1
    print(c[idx:fim])
else:
    print("[ERRO] Funcao gerarPDF nao encontrada no HTML.")

print("\n" + "=" * 70)
print("2) TODAS AS ROTAS DE PDF DO BP NO MAIN.PY")
print("=" * 70)
c_backend = open(r"pc_backend\main.py", encoding="utf-8-sig").read()
for i, ln in enumerate(c_backend.split("\n"), 1):
    if "@app.get" in ln and ("pdf" in ln.lower() and "bp" in ln.lower()):
        print(f"  Linha {i}: {ln.strip()}")
