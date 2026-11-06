import shutil, glob, os

backups = sorted(glob.glob("pc_frontend/index.html.bak_reconstruir_*"), key=os.path.getmtime)
if not backups:
    print("[ERRO] Backup nao encontrado.")
    exit(1)

bak = backups[-1]
shutil.copy2(bak, "pc_frontend/index.html")
print(f"[OK] index.html restaurado de: {bak}")

# Faz o mesmo para normas.html
backups_normas = sorted(glob.glob("pc_frontend/normas.html.bak_reconstruir_*"), key=os.path.getmtime)
if backups_normas:
    bak_n = backups_normas[-1]
    shutil.copy2(bak_n, "pc_frontend/normas.html")
    print(f"[OK] normas.html restaurado de: {bak_n}")
