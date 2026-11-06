import shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_linha353_{ts}")

linhas = open(back_path, encoding='utf-8-sig').read().split('\n')

# Mostra o contexto atual (linhas 345 a 360)
print("--- CONTEXTO ATUAL (linhas 345-360) ---")
for i in range(344, min(360, len(linhas))):
    print(f"{i+1:>4}: {linhas[i]}")

# Localiza a linha que tem 'pdf.multi_cell(col_w[j], 4, h' e substitui
alterou = False
for i, ln in enumerate(linhas):
    if 'pdf.multi_cell(col_w[j], 4, h' in ln and '_limpar_ascii' not in ln:
        # Pega a indentação original
        indent = ln[:len(ln) - len(ln.lstrip())]
        # Substitui
        linhas[i] = indent + 'pdf.multi_cell(col_w[j], 4, _limpar_ascii(h), border=0, align="C")'
        alterou = True
        print(f"\n[OK] Linha {i+1} substituída:")
        print(f"   ANTES: {ln.strip()}")
        print(f"   DEPOIS: {linhas[i].strip()}")

if not alterou:
    print("\n[AVISO] Não encontrei a linha 'pdf.multi_cell(col_w[j], 4, h' para substituir.")
    # Fallback: tenta também sem espaço
    for i, ln in enumerate(linhas):
        if 'multi_cell(col_w[j], 4, h' in ln:
            indent = ln[:len(ln) - len(ln.lstrip())]
            linhas[i] = indent + 'pdf.multi_cell(col_w[j], 4, _limpar_ascii(h), border=0, align="C")'
            print(f"[OK] Substituído (fallback): linha {i+1}")

# Salva
c = '\n'.join(linhas)
open(back_path, 'w', encoding='utf-8').write(c)

# Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("\n[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_linha353_{ts}", back_path)
    print("[OK] Backup restaurado")
