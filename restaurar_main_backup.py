import shutil, glob, os

# Restaura o main.py do backup mais recente
backups = sorted(glob.glob(r"pc_backend\main.py.bak_buscar_bp2_*"), key=os.path.getmtime)
if not backups:
    print("[ERRO] Backup nao encontrado.")
else:
    bak = backups[-1]
    shutil.copy2(bak, r"pc_backend\main.py")
    print(f"[OK] main.py restaurado de: {bak}")

# Verifica se a sintaxe esta OK
import ast
try:
    ast.parse(open(r"pc_backend\main.py", encoding="utf-8").read())
    print("[OK] Sintaxe do main.py esta correta.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe ainda quebrada: {e}")
