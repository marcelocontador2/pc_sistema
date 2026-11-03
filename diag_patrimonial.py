import re

print("=" * 70)
print("DIAGNÓSTICO: ANÁLISE PATRIMONIAL")
print("=" * 70)

# 1. Como a rota está no Backend?
c_back = open(r"pc_backend\main.py", encoding="utf-8-sig").read()
print("\n--- ROTA NO BACKEND ---")
rotas = re.findall(r'@app\.(?:get|post)\(["\'](/gerar_pdf[^"\']*patrimonial[^"\']*)["\']\)\s*\ndef\s+(\w+)\(([^)]*)\)', c_back)
if rotas:
    for rota, func, args in rotas:
        print(f"Rota: {rota}")
        print(f"Função: {func}({args})")
        if "{id}" in rota or "id:" in args or "historico_id" in args:
            print("-> [STATUS] A rota espera o ID no path ou parâmetro!")
        else:
            print("-> [STATUS] A rota NÃO espera ID (gera sempre o atual).")
else:
    print("Nenhuma rota de PDF para patrimonial encontrada.")

# 2. Como o botão está no Frontend?
print("\n--- BOTÃO NO FRONTEND (analise_patrimonial.html) ---")
try:
    c_front = open(r"pc_frontend\analise_patrimonial.html", encoding="utf-8").read()
    # Procura a chamada do botão
    match_btn = re.search(r'onclick="[^"]*(?:gerar_pdf|gerarPDF|window\.open)[^"]*"', c_front, re.IGNORECASE)
    if match_btn:
        print(f"Chamada atual do botão: {match_btn.group(0)}")
    else:
        print("Não achei chamada onclick de PDF no botão.")
except Exception as e:
    print(f"Erro ao ler o arquivo HTML: {e}")
