c = open('dashboard_despesas.html', encoding='utf-8').read()

termo_antigo = "2. Despesas de Capital (Investimentos + Inversões + Amortização)"
termo_novo = "2. Despesas de Capital (Investimentos + Inversões)"

if termo_antigo in c:
    c = c.replace(termo_antigo, termo_novo)
    open('dashboard_despesas.html', 'w', encoding='utf-8').write(c)
    print("[OK] Termo 'Amortização' removido do título!")
else:
    print("[AVISO] Texto não encontrado. Verifique se a grafia está igual no HTML.")
