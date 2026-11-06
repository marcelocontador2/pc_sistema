c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("1) O link 'analise_bp' está no HTML?")
print("=" * 70)
if 'href="/analise_bp"' in c:
    print("[SIM] O link 'analise_bp' existe.")
    idx = c.find('href="/analise_bp"')
    print("Trecho:", c[max(0, idx-100):idx+200])
else:
    print("[NAO] O link 'analise_bp' nao existe.")

print("\n" + "=" * 70)
print("2) A lista 'linksParaMover' contém 'Análise BP'?")
print("=" * 70)
if 'linksParaMover' in c:
    idx = c.find('linksParaMover')
    fim = c.find('];', idx) + 2
    trecho = c[idx:fim]
    print("Trecho da lista:", trecho)
    if "'Análise BP'" in trecho:
        print("[SIM] 'Análise BP' está na lista.")
    else:
        print("[NAO] 'Análise BP' NAO está na lista.")
else:
    print("[NAO] A lista 'linksParaMover' nao existe.")
