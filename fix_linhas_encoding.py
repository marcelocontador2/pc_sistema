import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_linhas_{ts}")
linhas = open(back_path, encoding='utf-8-sig').read().split('\n')

print("--- PROCURANDO LINHAS 349 e 358 ---")

# Encontra a linha que tem "periodo_formatado" e "cell(85, 6" (linha 349)
alterou = 0
for i, ln in enumerate(linhas):
    # Linha 349: pdf.cell(85, 6, f"Período: {periodo_formatado}"...
    if 'cell(85, 6' in ln and 'periodo_formatado' in ln and '_limpar_ascii' not in ln:
        indent = ln[:len(ln) - len(ln.lstrip())]
        linhas[i] = indent + 'pdf.cell(85, 6, _limpar_ascii(f"Periodo: {periodo_formatado}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")'
        print(f"[OK] Linha {i+1} substituída: {linhas[i].strip()}")
        alterou += 1
    
    # Linha 358: pdf.cell(0, 5, f"COFEN/BR - {titulo_pdf} - Período: {periodo_formatado} (Continuação)"...
    if 'cell(0, 5' in ln and 'titulo_pdf' in ln and 'periodo_formatado' in ln and '_limpar_ascii' not in ln:
        indent = ln[:len(ln) - len(ln.lstrip())]
        linhas[i] = indent + 'pdf.cell(0, 5, _limpar_ascii(f"COFEN/BR - {titulo_pdf} - Periodo: {periodo_formatado} (Continuacao)"),'
        print(f"[OK] Linha {i+1} substituída: {linhas[i].strip()}")
        alterou += 1

if alterou == 0:
    print("[AVISO] Nenhuma linha encontrada. Mostrando contexto das linhas próximas...")
    for i, ln in enumerate(linhas, 1):
        if 'cell(85, 6' in ln or ('cell(0, 5' in ln and 'titulo_pdf' in ln):
            print(f"  Linha {i}: {repr(ln)}")

# Salva
c = '\n'.join(linhas)
open(back_path, 'w', encoding='utf-8').write(c)

# Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print(f"\n[OK] Sintaxe validada ({alterou} linhas alteradas)")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_linhas_{ts}", back_path)
    print("[OK] Backup restaurado")
