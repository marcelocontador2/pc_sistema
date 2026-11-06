import os, glob, shutil

# 1. Restaura o backup mais recente que contém o download_pdf íntegro
backups = sorted(glob.glob(r"pc_backend\main.py.bak_dmpl_*"), reverse=True)
if not backups:
    print("[ERRO] Nenhum backup encontrado.")
    exit(1)

ultimo = backups[0]
shutil.copy2(ultimo, r"pc_backend\main.py")
print(f"[OK] Restaurado do backup: {ultimo}")
