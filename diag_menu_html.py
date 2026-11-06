c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()
# Acha o trecho em volta de "Demonstra"
idx = c.find("Demonstra")
if idx != -1:
    print("Trecho ao redor de 'Demonstra' no index.html:")
    print(repr(c[max(0, idx-200):idx+300]))
