import re

c = open('dashboard_despesas.html', encoding='utf-8').read()

# Expressão regular para achar e remover os blocos 3 e 4 de renderização
padrao = r'// 3\. Pessoal.*?pInvest\.empenhado\);'
c_novo = re.sub(padrao, '', c, flags=re.DOTALL)

if c_novo != c:
    open('dashboard_despesas.html', 'w', encoding='utf-8').write(c_novo)
    print("[OK] Blocos de 'Pessoal' e 'Investimentos' removidos da tela com sucesso!")
else:
    print("[AVISO] Trecho não encontrado. Verifique se o arquivo foi alterado manualmente.")
