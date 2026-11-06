import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_remove_rodape_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# O trecho que desenha o rodape no PDF da DFC
antigo = '''    pdf.ln(15)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 5, "Relatorio gerado automaticamente pelo Sistema SIGPC/COFEN", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
'''

# Substitui por vazio
novo = ""

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(back_path, "w", encoding="utf-8").write(c)
    print("[OK] Rodape removido com sucesso.")
else:
    print("[AVISO] Trecho exato nao encontrado. Tentando buscar apenas a linha do cell...")
    # Tenta remover so a linha do pdf.cell
    antigo2 = '    pdf.cell(0, 5, "Relatorio gerado automaticamente pelo Sistema SIGPC/COFEN", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")\n'
    if antigo2 in c:
        c = c.replace(antigo2, "", 1)
        open(back_path, "w", encoding="utf-8").write(c)
        print("[OK] Linha do rodape removida (variacao).")
    else:
        print("[ERRO] Nao foi possivel encontrar a linha para remover.")

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_remove_rodape_{ts}", back_path)
    print("[OK] Backup restaurado.")
