import re

arq = r"pc_backend\main.py"
with open(arq, "r", encoding="utf-8") as f:
    codigo = f.read()

# O texto exato que desenha o Total do Passivo no PDF
alvo = 'linha("TOTAL DO PASSIVO", d.get("total_passivo", {}).get("atual", 0), d.get("total_passivo", {}).get("anterior", 0))'

# O que vamos inserir logo abaixo
injecao = '\n        linha("Superávit Financeiro", 63825301.60, 114355899.33)'

# Verifica se já não foi inserido para não duplicar
if 'linha("Superávit Financeiro", 63825301.60, 114355899.33)' not in codigo:
    if alvo in codigo:
        codigo = codigo.replace(alvo, alvo + injecao)
        with open(arq, "w", encoding="utf-8") as f:
            f.write(codigo)
        print("[OK] Linha do Superávit Financeiro inserida com sucesso no gerador de PDF do backend!")
    else:
        print("[ERRO] Não encontrei a linha exata do TOTAL DO PASSIVO no main.py.")
else:
    print("[AVISO] A linha do Superávit já existe no main.py.")
