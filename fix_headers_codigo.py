import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_headers_corrigidos_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Corrige os headers que estão com encoding duplo no código
correcoes = [
    ("ESPECIFICAÃ‡ÃƒO (ATIVO)", "ESPECIFICACAO (ATIVO)"),
    ("ESPECIFICAÃ‡ÃƒO (PASSIVO)", "ESPECIFICACAO (PASSIVO)"),
    ("ESPECIFICAÃ‡ÃƒO (INGRESSOS)", "ESPECIFICACAO (INGRESSOS)"),
    ("ESPECIFICAÃ‡ÃƒO (DISPÃŠNDIOS)", "ESPECIFICACAO (DISPENDIOS)"),
    ("ESPECIFICAÃ‡ÃƒO", "ESPECIFICACAO"),
    ("PREVISÃƒO INICIAL", "PREVISAO INICIAL"),
    ("PREVISÃƒO ATUALIZADA", "PREVISAO ATUALIZADA"),
    ("DÃ‰BITOS", "DEBITOS"),
    ("CRÃ‰DITOS", "CREDITOS"),
    ("PATRIMÃ”NIO SOCIAL", "PATRIMONIO SOCIAL"),
    ("AJUSTES DE AVALIAÃ‡ÃƒO", "AJUSTES DE AVALIACAO"),
    ("VARIAÃ‡Ã•ES AUMENTATIVAS", "VARIACOES AUMENTATIVAS"),
    ("VARIAÃ‡Ã•ES DIMINUTIVAS", "VARIACOES DIMINUTIVAS"),
]

for antigo, novo in correcoes:
    if antigo in c:
        c = c.replace(antigo, novo)
        print(f"[OK] Corrigido: {antigo} -> {novo}")

# Salva
open(back_path, 'w', encoding='utf-8').write(c)

# Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("\n[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_headers_corrigidos_{ts}", back_path)
    print("[OK] Backup restaurado")
