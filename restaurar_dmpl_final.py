import os, glob, shutil

# Restaura o backup mais recente
backups = sorted(glob.glob(r"pc_backend\main.py.bak_dmpl_final_*"), reverse=True)
if not backups:
    print("[ERRO] Nenhum backup encontrado.")
    exit(1)

ultimo = backups[0]
shutil.copy2(ultimo, r"pc_backend\main.py")
print(f"[OK] Restaurado do backup: {ultimo}")
