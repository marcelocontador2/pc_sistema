c = open('main.py', encoding='utf-8-sig').read()

# Corrige a condição para aceitar tanto "Centro de Custos" quanto "CENTRO_CUSTOS"
c = c.replace(
    'if tipo_relatorio == "Centro de Custos":',
    'if tipo_relatorio and (tipo_relatorio.upper() == "CENTRO_CUSTOS" or tipo_relatorio == "Centro de Custos"):'
)

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] Condição do tipo_relatorio corrigida!")
