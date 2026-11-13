with open("pc_frontend/analise_comparativo_receitas.html", "r", encoding="utf-8") as f:
    html = f.read()

# Mostra a função salvarAtual
idx = html.find("function salvarAtual()")
if idx != -1:
    print("📄 Função salvarAtual():")
    print("-" * 80)
    i = html.find("{", idx)
    contador = 1
    i += 1
    while i < len(html) and contador > 0:
        if html[i] == "{": contador += 1
        elif html[i] == "}": contador -= 1
        i += 1
    print(html[idx:i])
    print("-" * 80)
else:
    print("❌ Função salvarAtual() não encontrada.")
