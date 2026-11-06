import shutil, glob, os

# Acha o backup mais recente (feito antes da alteração do salvarMatriz)
backups = sorted(glob.glob("pc_frontend/integridade.html.bak_carregar_*"), key=os.path.getmtime)
if not backups:
    print("[ERRO] Backup nao encontrado.")
    exit(1)

bak = backups[-1]
shutil.copy2(bak, "pc_frontend/integridade.html")
print(f"[OK] Arquivo restaurado de: {bak}")
