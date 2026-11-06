c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

idx = c.find("function excluirRelatorio")
if idx != -1:
    print("Função excluirRelatorio encontrada no index.html:")
    # Pega até 800 chars depois
    print(c[idx:idx+800])
else:
    print("Função excluirRelatorio NÃO encontrada no index.html (pode estar em outro arquivo JS).")
