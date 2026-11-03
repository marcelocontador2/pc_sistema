c = open('dashboard_despesas.html', encoding='utf-8').read()

antigo_bloco = """                // Bloco 1: Despesas de Capital (Topo)
                html += gerarBloco(
                    "Despesas de Capital (Investimentos + Inversões + Amortização)", 
                    "capital", 
                    aCapitalOrc, aCapitalEmp, pCapitalOrc, pCapitalEmp
                );

                // Bloco 2: Despesas Correntes
                html += gerarBloco(
                    "Despesas Correntes (Pessoal + Outras + Juros)", 
                    "corrente", 
                    aCorrenteOrc, aCorrenteEmp, pCorrenteOrc, pCorrenteEmp
                );"""

novo_bloco = """                // Bloco 1: Despesas Correntes
                html += gerarBloco(
                    "1. DESPESAS CORRENTES (Pessoal + Outras + Juros)", 
                    "corrente", 
                    aCorrenteOrc, aCorrenteEmp, pCorrenteOrc, pCorrenteEmp
                );

                // Bloco 2: Despesas de Capital
                html += gerarBloco(
                    "2. DESPESAS DE CAPITAL (Investimentos + Inversões + Amortização)", 
                    "capital", 
                    aCapitalOrc, aCapitalEmp, pCapitalOrc, pCapitalEmp
                );"""

if antigo_bloco in c:
    c = c.replace(antigo_bloco, novo_bloco)
    open('dashboard_despesas.html', 'w', encoding='utf-8').write(c)
    print("[OK] Ordem invertida: Correntes (1) no topo, Capital (2) abaixo!")
else:
    print("[AVISO] O bloco antigo não foi encontrado. Tentando substituição direta...")
    # Fallback caso o texto tenha mudado por algum motivo
    c = c.replace('"Despesas de Capital (Investimentos + Inversões + Amortização)"', '"2. DESPESAS DE CAPITAL (Investimentos + Inversões + Amortização)"')
    c = c.replace('"Despesas Correntes (Pessoal + Outras + Juros)"', '"1. DESPESAS CORRENTES (Pessoal + Outras + Juros)"')
    open('dashboard_despesas.html', 'w', encoding='utf-8').write(c)
    print("[OK] Títulos numerados aplicados (verifique se a ordem visual ficou correta).")
