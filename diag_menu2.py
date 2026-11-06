c = open("pc_frontend/analise_patrimonial.html", encoding="utf-8", errors="ignore").read()
idx = c.find('id="menu-demonstracoes"')
if idx != -1:
    print(repr(c[max(0, idx-150):idx+250]))
else:
    print("[AVISO] Nao encontrado nesse arquivo.")
