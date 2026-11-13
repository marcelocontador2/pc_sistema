import re

c = open('dashboard_despesas.html', encoding='utf-8').read()

# 1. Adiciona a classe CSS para o card de Total Geral (se ainda não existir)
if ".card.total-geral" not in c:
    css_alvo = "/* Cores específicas dos cards */"
    css_novo = css_alvo + "\n        .card.total-geral { border-top-color: #2d3748; background-color: #edf2f7; }"
    c = c.replace(css_alvo, css_novo)

# 2. Adiciona os cálculos do Total Geral
# Vamos procurar a declaração do pCapitalEmp e inserir os totais logo depois
padrao_calc = r'(const pCapitalEmp = pInvest\.empenhado \+ pInversoes\.empenhado \+ pAmort\.empenhado;)'
calc_total = r'''\1
                
                // Cálculos do Total Geral
                const aTotalOrc = aCorrenteOrc + aCapitalOrc;
                const aTotalEmp = aCorrenteEmp + aCapitalEmp;
                const pTotalOrc = pCorrenteOrc + pCapitalOrc;
                const pTotalEmp = pCorrenteEmp + pCapitalEmp;'''
c = re.sub(padrao_calc, calc_total, c)

# 3. Adiciona a chamada do Bloco 3 logo após o Bloco 2
padrao_bloco2 = r'(html \+= gerarBloco\("2\. Despesas de Capital.*?\);)(\s*)(painel\.innerHTML = html;)'
novo_bloco = r'''\1\2
                // 3. Total Geral
                html += gerarBloco("TOTAL GERAL DAS DESPESAS (Correntes + Capital)", "total-geral", aTotalOrc, aTotalEmp, pTotalOrc, pTotalEmp);
                
                \3'''
c = re.sub(padrao_bloco2, novo_bloco, c, flags=re.DOTALL)

open('dashboard_despesas.html', 'w', encoding='utf-8').write(c)
print("[OK] Terceira linha (Total Geral) adicionada com sucesso!")
