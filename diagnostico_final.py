c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("ESTRUTURA DO MENU ATUAL (apos git checkout)")
print("=" * 70)

idx = c.find('Importar Relatórios')
if idx != -1:
    print(c[max(0, idx-200):idx+2500])
else:
    print("[ERRO] Nao encontrei 'Importar Relatórios' no HTML.")

print("\n" + "=" * 70)
print("O link do DFC (analise_dfc) aparece no HTML?")
print("=" * 70)
if 'analise_dfc' in c:
    print("SIM! Ja existe.")
    i = c.find('analise_dfc')
    print(c[max(0, i-100):i+200])
else:
    print("NAO! Precisa ser inserido.")
