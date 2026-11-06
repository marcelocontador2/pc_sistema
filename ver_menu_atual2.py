c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

# Mostra o bloco do menu principal (do logo até o fim)
idx = c.find('<aside')
if idx == -1:
    idx = c.find('Importar Relatórios')

if idx != -1:
    print("=" * 70)
    print("MENU ATUAL (trecho)")
    print("=" * 70)
    print(c[idx:idx+2500])
else:
    print("[ERRO] Nao encontrei o menu.")
