c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

# Acha o bloco do menu (do "Análises Contábeis" até "Comparativo de Despesas")
idx_ini = c.find('Análises Contábeis')
idx_fim = c.find('Comparativo de Despesas', idx_ini)

if idx_ini != -1 and idx_fim != -1:
    print("=" * 70)
    print("TRECHO EXATO DO MENU (do titulo ate o fim das analises)")
    print("=" * 70)
    print(c[idx_ini:idx_fim+30])
else:
    print("[ERRO] Nao encontrei o bloco do menu.")
