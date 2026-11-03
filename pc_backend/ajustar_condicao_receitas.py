c = open('main.py', encoding='utf-8-sig').read()

# Ajusta a condição para aceitar "COMPARATIVO_RECEITAS" ou "Comparativo de Receitas"
c = c.replace(
    'if tipo_relatorio and tipo_relatorio.upper() == "COMPARATIVO_RECEITAS":',
    'if tipo_relatorio and ("COMPARATIVO_RECEITAS" in tipo_relatorio.upper() or "COMPARATIVO DE RECEITAS" in tipo_relatorio.upper()):'
)

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] Condição ajustada para aceitar variações do tipo!")
