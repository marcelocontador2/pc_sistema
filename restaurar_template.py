import glob, os, shutil, datetime

# 1. Salva o template quebrado como backup
arq = r"pc_frontend\relatorio_consolidado_template.html"
shutil.copy2(arq, f"pc_frontend\\relatorio_consolidado_template_BROKEN_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

# 2. Restaura do backup mais recente que NÃO seja o BROKEN
backups = glob.glob(r"pc_frontend\relatorio_consolidado_template_BROKEN_*.html") + \
          glob.glob(r"pc_frontend\relatorio_consolidado_template.bak_*.html")

# Remove o backup que acabamos de criar (BROKEN) da lista
backups = [b for b in backups if "BROKEN" not in b]

if backups:
    backup = max(backups, key=os.path.getctime)
    print(f"[OK] Restaurando de: {backup}")
    shutil.copy2(backup, arq)
    print("[OK] Template restaurado.")
else:
    print("[AVISO] Nenhum backup encontrado. Tentando outro método...")
