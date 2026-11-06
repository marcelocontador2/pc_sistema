c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()
idx = c.find('Análises Contábeis')
if idx != -1:
    print("Trecho do menu (a partir de 'Análises Contábeis'):")
    print(c[idx:idx+2000])
else:
    print("[ERRO] Nao encontrei 'Análises Contábeis' no HTML.")
