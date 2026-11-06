c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("1) O link 'analise_bp' existe no HTML?")
print("=" * 70)
if 'href="/analise_bp"' in c:
    print("[SIM] O link 'analise_bp' ja existe.")
else:
    print("[NAO] O link 'analise_bp' nao existe.")

print("\n" + "=" * 70)
print("2) O link 'analise_financeira_bf' existe no HTML?")
print("=" * 70)
if 'href="/analise_financeira_bf"' in c:
    print("[SIM] O link do BF existe.")
else:
    print("[NAO] O link do BF nao existe.")

print("\n" + "=" * 70)
print("3) A lista 'linksParaMover' existe no HTML?")
print("=" * 70)
if 'linksParaMover' in c:
    print("[SIM] A lista 'linksParaMover' existe.")
    idx = c.find('linksParaMover')
    print("Trecho:", c[idx:idx+300])
else:
    print("[NAO] A lista 'linksParaMover' nao existe.")

print("\n" + "=" * 70)
print("4) O submenu 'Análises Contábeis' (ou 'AnÃ¡lises') existe?")
print("=" * 70)
if 'Análises Contábeis' in c:
    print("[SIM] 'Análises Contábeis' existe.")
elif 'AnÃ¡lises ContÃ¡beis' in c:
    print("[SIM] 'AnÃ¡lises ContÃ¡beis' (corrompido) existe.")
else:
    print("[NAO] O submenu nao existe.")

print("\n" + "=" * 70)
print("5) Como está a estrutura do menu? (primeiras 20 linhas com <li> e <a>)")
print("=" * 70)
linhas = c.split("\n")
cont = 0
for i, ln in enumerate(linhas):
    if ('<li>' in ln or '<a ' in ln) and ('href=' in ln):
        print(f"  Linha {i+1}: {ln.strip()[:150]}")
        cont += 1
        if cont >= 20:
            print("  ... (mais linhas)")
            break
