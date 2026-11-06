c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()
idx = c.find('Relatorio Consolidado')
if idx != -1:
    print("Trecho do menu (apos Relatorio Consolidado):")
    print(c[idx:idx+1500])
else:
    print("[ERRO] Nao encontrei 'Relatorio Consolidado'.")
