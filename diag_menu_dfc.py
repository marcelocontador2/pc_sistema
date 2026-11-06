c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("PROCURANDO O LINK DO BF NO INDEX.HTML")
print("=" * 70)
idx = c.find("analise_financeira_bf")
if idx != -1:
    print(f"Encontrado na posicao {idx}. Trecho:")
    print(repr(c[max(0, idx-300):idx+300]))
else:
    print("[AVISO] 'analise_financeira_bf' nao encontrado no index.html.")
    print("Procurando por 'Análise Financeira'...")
    idx2 = c.find("Análise Financeira")
    if idx2 != -1:
        print(repr(c[max(0, idx2-300):idx2+300]))
    else:
        print("[AVISO] 'Análise Financeira' tambem nao encontrado.")

print("\n" + "=" * 70)
print("VERIFICANDO SE O LINK DA DFC FOI INSERIDO")
print("=" * 70)
if 'analise_dfc' in c:
    idx = c.find("analise_dfc")
    print(f"Encontrado na posicao {idx}. Trecho:")
    print(repr(c[max(0, idx-300):idx+300]))
else:
    print("[AVISO] O link 'analise_dfc' NAO esta no index.html.")
