import glob, os, shutil

# Encontra o backup mais recente feito ANTES da tentativa de paisagem
backups = glob.glob(r"pc_backend\main_backup_paisagem_*.py")
if not backups:
    print("[ERRO] Backup da tentativa de paisagem não encontrado.")
    exit()

backup = max(backups, key=os.path.getctime)
print(f"[OK] Restaurando de: {backup}")
shutil.copy2(backup, r"pc_backend\main.py")

# Valida a sintaxe
with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

try:
    compile(codigo, "main.py", "exec")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO] Backup quebrado na linha {e.lineno}: {e.msg}")
    exit()

print("[OK] main.py restaurado para o estado funcional (capa em retrato, sem 'Executiva').")
