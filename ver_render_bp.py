c = open("pc_frontend/analise_bp.html", encoding="utf-8", errors="ignore").read()

# Procura o trecho do render onde os campos sao acessados
idx = c.find("let html = '';")
if idx != -1:
    fim = c.find("tb.innerHTML = html;", idx) + 20
    print("=" * 70)
    print("TRECHO DO RENDER (onde os campos sao acessados)")
    print("=" * 70)
    print(c[idx:fim])
else:
    print("[ERRO] Trecho do render nao encontrado.")
