import re, shutil, datetime, glob, os

# 1. Restaura o backup anterior
backups = glob.glob(r"pc_backend\main_backup_consolidado_homogeneo_*.py")
if backups:
    backup = max(backups, key=os.path.getctime)
    print(f"[OK] Restaurando de: {backup}")
    shutil.copy2(backup, r"pc_backend\main.py")
else:
    print("[AVISO] Backup não encontrado. Continuando com o main.py atual.")

# 2. Carrega o código
with open(r"pc_backend\main.py", "r", encoding="utf-8") as f:
    codigo = f.read()

# 3. Valida que está tudo OK
try:
    compile(codigo, "main.py", "exec")
    print("[OK] main.py íntegro após restauração.")
except SyntaxError as e:
    print(f"[ERRO] O backup também está quebrado na linha {e.lineno}: {e.msg}")
    print("[INFO] Restaurando de um backup mais antigo...")
    backups_antigos = sorted(glob.glob(r"pc_backend\main_backup_*.py"), key=os.path.getctime, reverse=True)
    for b in backups_antigos:
        try:
            with open(b, "r", encoding="utf-8") as f:
                teste = f.read()
            compile(teste, b, "exec")
            shutil.copy2(b, r"pc_backend\main.py")
            print(f"[OK] Restaurado de: {b}")
            codigo = teste
            break
        except:
            continue
    else:
        print("[ERRO] Nenhum backup íntegro encontrado.")
        exit()

print("[OK] Pronto. O main.py está no estado anterior.")
