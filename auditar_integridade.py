import os, re

print("=" * 70)
print("AUDITORIA: TELA DE INTEGRIDADE")
print("=" * 70)

# 1. Procurar rotas de PDF no Backend
back_path = r"pc_backend\main.py"
c_back = open(back_path, encoding='utf-8-sig').read()

print("\n--- ROTAS DE PDF NO BACKEND ---")
rotas = re.findall(r'@app\.(?:get|post)\(["\'](/gerar_pdf[^"\']*integridade[^"\']*)["\']\)\s*\ndef\s+(\w+)\(([^)]*)\)', c_back)
if rotas:
    for rota, func, args in rotas:
        print(f"Rota: {rota}")
        print(f"Função: {func}({args})")
else:
    print("Nenhuma rota de PDF específica para 'integridade' encontrada no main.py.")

# 2. Procurar comportamento no HTML
print("\n--- TELA HTML (integridade.html) ---")
front_path = r"pc_frontend\integridade.html"

if not os.path.exists(front_path):
    print("[ERRO] Arquivo integridade.html não encontrado.")
else:
    c = open(front_path, encoding='utf-8').read()
    
    tem_historico = 'name="historico"' in c or 'historico-lista' in c or 'radio' in c
    print(f" - Tem caixa de Histórico Salvo / Seleção? {'SIM' if tem_historico else 'NÃO'}")
    
    # Como chama o PDF?
    if 'window.print()' in c:
        print(" - Como gera PDF: window.print() (Nativo)")
    elif 'gerar_pdf' in c:
        match = re.search(r'.{0,80}gerar_pdf[^"\']*.{0,80}', c)
        print(f" - Como gera PDF: Chama Rota")
        print(f"   Trecho: {match.group(0).strip()}")
    else:
        print(" - Como gera PDF: Não encontrado.")
