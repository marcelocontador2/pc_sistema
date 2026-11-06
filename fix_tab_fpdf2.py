import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_tab2_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Verifica o que está na linha 109 e 130 agora
linhas = c.split('\n')
print("--- ANTES DA CORREÇÃO ---")
print(f"Linha 109: {linhas[108].strip()}")
print(f"Linha 130: {linhas[129].strip()}")

# 1. Correção da linha 109 (dentro do draw_row)
antigo_109 = "                    txt = str(row[j]).encode('latin-1', 'replace').decode('latin-1') or \" \""
novo_109 = """                    txt_raw = str(row[j])
                    txt_raw = txt_raw.replace(chr(9), ' ').replace(chr(10), ' ').replace(chr(13), ' ')
                    txt_raw = ''.join(ch if ord(ch) >= 32 else ' ' for ch in txt_raw)
                    txt = txt_raw.encode('latin-1', 'replace').decode('latin-1') or " \""""

if antigo_109 in c:
    c = c.replace(antigo_109, novo_109, 1)
    print("[OK] Linha 109 corrigida")
else:
    print("[AVISO] Linha 109 não encontrada com o texto exato. Tentando variação...")

# 2. Correção da linha 130 (dentro do draw_row, ao escrever)
antigo_130 = "                txt = str(row[j]).encode('latin-1', 'replace').decode('latin-1')"
novo_130 = """                txt_raw = str(row[j])
                txt_raw = txt_raw.replace(chr(9), ' ').replace(chr(10), ' ').replace(chr(13), ' ')
                txt_raw = ''.join(ch if ord(ch) >= 32 else ' ' for ch in txt_raw)
                txt = txt_raw.encode('latin-1', 'replace').decode('latin-1')"""

if antigo_130 in c:
    c = c.replace(antigo_130, novo_130, 1)
    print("[OK] Linha 130 corrigida")
else:
    print("[AVISO] Linha 130 não encontrada com o texto exato")

# Salva
open(back_path, 'w', encoding='utf-8').write(c)

# Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("\n[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_tab2_{ts}", back_path)
    print("[OK] Backup restaurado")

# Mostra o que ficou
linhas_depois = open(back_path, encoding='utf-8').read().split('\n')
print("\n--- DEPOIS DA CORREÇÃO ---")
for i, ln in enumerate(linhas_depois, 1):
    if 'txt_raw' in ln or ('txt = ' in ln and 'latin-1' in ln):
        print(f"Linha {i}: {ln.strip()}")
