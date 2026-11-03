import shutil, datetime

# Backup
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2("main.py", f"main.py.bak_{ts}")
print(f"[OK] Backup: main.py.bak_{ts}")

c = open("main.py", encoding="utf-8-sig").read()

# Ancora exata: o final da branch de receitas
ancora = '''        nome_arquivo = f"COMPARATIVO_RECEITAS_{periodo_str}.csv"'''

if "COMPARATIVO_DESPESAS_{periodo_str}" in c:
    print("[!] Branch de despesas ja existe. Nada a fazer.")
elif ancora not in c:
    print("[ERRO] Ancora nao encontrada. Me mande a saida do ver_upload.py.")
else:
    novo = ancora + '''
    if tipo_relatorio and ("COMPARATIVO_DESPESAS" in tipo_relatorio.upper() or "COMPARATIVO DE DESPESAS" in tipo_relatorio.upper()):
        periodo_str = f"{ano}_{periodo_tipo}_{periodo_valor}" if ano and periodo_tipo and periodo_valor else "2026_TRIMESTRE_3"
        nome_arquivo = f"COMPARATIVO_DESPESAS_{periodo_str}.csv"'''
    c = c.replace(ancora, novo, 1)
    open("main.py", "w", encoding="utf-8").write(c)
    print("[OK] Branch COMPARATIVO_DESPESAS adicionada ao /upload!")

# Valida sintaxe
import ast
ast.parse(open("main.py", encoding="utf-8").read())
print("[OK] Sintaxe OK!")
