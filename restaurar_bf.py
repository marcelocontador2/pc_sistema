import shutil, glob, os

backups = sorted(glob.glob("pc_frontend/analise_financeira_bf.html.bak_render_total_*"), key=os.path.getmtime)
if not backups:
    print("[ERRO] Backup nao encontrado.")
    exit(1)

bak = backups[-1]
shutil.copy2(bak, "pc_frontend/analise_financeira_bf.html")
print(f"[OK] Arquivo restaurado de: {bak}")
