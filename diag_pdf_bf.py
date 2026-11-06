c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

# Procura a rota de gerar PDF do BF
idx = c.find('@app.get("/gerar_pdf_analise_financeira_bf/{id}")')
if idx != -1:
    fim = c.find('@app', idx + 10)
    if fim == -1: fim = idx + 2000
    trecho = c[idx:fim]
    
    print("=" * 70)
    print("TRECHO DA ROTA DO PDF DO BF")
    print("=" * 70)
    print(trecho)
else:
    print("[ERRO] Rota /gerar_pdf_analise_financeira_bf nao encontrada.")
