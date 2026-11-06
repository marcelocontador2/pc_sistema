c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("1) O link 'analise_dfc' aparece no HTML?")
print("=" * 70)
if 'analise_dfc' in c:
    idx = c.find('analise_dfc')
    print("SIM! Trecho encontrado:")
    print(repr(c[max(0, idx-200):idx+200]))
else:
    print("NAO! O link nao esta no HTML.")

print("\n" + "=" * 70)
print("2) O link 'analise_financeira_bf' aparece?")
print("=" * 70)
if 'analise_financeira_bf' in c:
    idx = c.find('analise_financeira_bf')
    print("SIM! Trecho encontrado:")
    print(repr(c[max(0, idx-200):idx+300]))
else:
    print("NAO! O link do BF nao esta no HTML.")

print("\n" + "=" * 70)
print("3) Quantas vezes 'analise_dfc' aparece?")
print("=" * 70)
print(c.count('analise_dfc'), "vezes")
