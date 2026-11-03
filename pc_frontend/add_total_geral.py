import re

c = open('dashboard_despesas.html', encoding='utf-8').read()

# 1. Adiciona a classe CSS para o card de Total Geral (cor escura para destaque)
css_alvo = ".card.investimento { border-top-color: #38a169; }"
css_novo = css_alvo + "\n        .card.total-geral { border-top-color: #2d3748; background-color: #f7fafc; }"
if ".card.total-geral" not in c:
    c = c.replace(css_alvo, css_novo)

# 2. Substitui o bloco de renderização para incluir os cálculos do Total Geral e a 3ª linha
antigo_rend = """// --- RENDERIZAÇÃO NA ORDEM EXATA ---
                let html = '';

                // 1. Correntes
                html += gerarBloco("1. Despesas Correntes (Pessoal + Outras + Juros)", "corrente", aCorrenteOrc, aCorrenteEmp, pCorrenteOrc, pCorrenteEmp);

                // 2. Capital
                html += gerarBloco("2. Despesas de Capital (Investimentos + Inversões)", "capital", aCapitalOrc, aCapitalEmp, pCapitalOrc, pCapitalEmp);

                painel.innerHTML = html;"""

novo_rend = """// --- CÁLCULOS DO TOTAL GERAL ---
                const aTotalOrc = aCorrenteOrc + aCapitalOrc;
                const aTotalEmp = aCorrenteEmp + aCapitalEmp;
                const pTotalOrc = pCorrenteOrc + pCapitalOrc;
                const pTotalEmp = pCorrenteEmp + pCapitalEmp;

                // --- RENDERIZAÇÃO NA ORDEM EXATA ---
                let html = '';

                // 1. Correntes
                html += gerarBloco("1. Despesas Correntes (Pessoal + Outras + Juros)", "corrente", aCorrenteOrc, aCorrenteEmp, pCorrenteOrc, pCorrenteEmp);

                // 2. Capital
                html += gerarBloco("2. Despesas de Capital (Investimentos + Inversões)", "capital", aCapitalOrc, aCapitalEmp, pCapitalOrc, pCapitalEmp);

                // 3. Total Geral
                html += gerarBloco("TOTAL GERAL DAS DESPESAS (Correntes + Capital)", "total-geral", aTotalOrc, aTotalEmp, pTotalOrc, pTotalEmp);

                painel.innerHTML = html;"""

if antigo_rend in c:
    c = c.replace(antigo_rend, novo_rend)
    open('dashboard_despesas.html', 'w', encoding='utf-8').write(c)
    print("[OK] Terceira linha (Total Geral) adicionada com sucesso!")
else:
    print("[ERRO] Não encontrei o bloco de renderização. O arquivo pode ter sido alterado.")
