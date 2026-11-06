import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_titulo_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Corrige os títulos no código (encoding duplo)
correcoes = [
    ('"BalanÃ§o OrÃ§amentÃ¡rio"', '"Balanço Orçamentário"'),
    ('"BalanÃ§o Patrimonial"', '"Balanço Patrimonial"'),
    ('"BalanÃ§o Financeiro"', '"Balanço Financeiro"'),
    ('"BalanÃ§o Comparativo"', '"Balanço Comparativo"'),
    ('"Balancete ContÃ¡bil"', '"Balancete Contábil"'),
    ('"DemonstraÃ§Ã£o das MutaÃ§Ãµes do PatrimÃ´nio LÃquido"', '"Demonstração das Mutações do Patrimônio Líquido"'),
    ('"DemonstraÃ§Ã£o do Fluxo de Caixa"', '"Demonstração do Fluxo de Caixa"'),
    ('"DemonstraÃ§Ã£o das VariaÃ§Ãµes Patrimoniais"', '"Demonstração das Variações Patrimoniais"'),
]

for antigo, novo in correcoes:
    if antigo in c:
        c = c.replace(antigo, novo)
        print(f"[OK] Corrigido: {antigo[:50]}... -> {novo[:50]}...")

# Salva
open(back_path, 'w', encoding='utf-8').write(c)

# Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("\n[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_titulo_{ts}", back_path)
    print("[OK] Backup restaurado")
