import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_fonte_bf_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

qtd = c.count("fonte_padrao")
print(f"[INFO] Encontradas {qtd} ocorrencias de 'fonte_padrao'.")

c = c.replace("fonte_padrao", '"Helvetica"')
open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] Sintaxe validada. 'fonte_padrao' substituido por 'Helvetica'.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_fonte_bf_{ts}", back_path)
    print("[OK] Backup restaurado.")
