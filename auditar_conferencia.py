import os, re

print("=" * 70)
print("AUDITORIA: TELA DE CONFERÊNCIA")
print("=" * 70)

# 1. Procurar rotas de PDF no Backend
back_path = r"pc_backend\main.py"
c_back = open(back_path, encoding='utf-8-sig').read()

print("\n--- ROTAS DE PDF NO BACKEND ---")
rotas = re.findall(r'@app\.(?:get|post)\(["\'](/gerar_pdf[^"\']*conferencia[^"\']*)["\']\)\s*\ndef\s+(\w+)\(([^)]*)\)', c_back)
if rotas:
    for rota, func, args in rotas:
        print(f"Rota: {rota}")
        print(f"Função: {func}({args})")
        if "historico_id" in args or "id:" in args:
            print("-> [STATUS] Já aceita ID do histórico!")
        else:
            print("-> [STATUS] NÃO aceita ID do histórico.")
else:
    print("Nenhuma rota de PDF específica para 'conferencia' encontrada no main.py.")

# 2. Procurar comportamento nos arquivos HTML
print("\n--- TELAS HTML (conferencia.html / conferencia_nova.html) ---")
front_dir = r"pc_frontend"
arquivos = ["conferencia.html", "conferencia_nova.html"]

for arq in arquivos:
    path = os.path.join(front_dir, arq)
    if not os.path.exists(path):
        print(f"\n[{arq}] Arquivo não encontrado.")
        continue
        
    c = open(path, encoding='utf-8').read()
    print(f"\n[{arq}]")
    
    # Verifica histórico
    tem_historico = 'name="historico"' in c or 'historico-lista' in c
    print(f" - Tem caixa de Histórico Salvo? {'SIM' if tem_historico else 'NÃO'}")
    
    # Verifica como gera o PDF
    if 'window.print()' in c:
        print(" - Como gera PDF: window.print() (Nativo) -> [STATUS] Já obedece ao histórico se atualizar a tela.")
    elif 'gerar_pdf' in c:
        # Tenta extrair a URL
        match = re.search(r'gerar_pdf[^"\']*', c)
        print(f" - Como gera PDF: Chama Rota ({match.group(0)})")
        
        # Verifica se envia historico_id
        if 'historico_id' in c:
            print(" - Envia o ID do histórico? SIM")
        else:
            print(" - Envia o ID do histórico? NÃO -> [STATUS] Precisa de ajuste!")
    else:
        print(" - Como gera PDF: Não encontrado ou usa outro método.")

