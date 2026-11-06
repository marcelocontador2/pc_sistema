import glob, os, shutil

arq = r"pc_frontend\relatorio_consolidado_template.html"
backups = glob.glob(r"pc_frontend\relatorio_consolidado_template_*.html")
backups = [b for b in backups if "BROKEN" not in b]

if not backups:
    print("[ERRO] Nenhum backup encontrado para restaurar.")
    exit()

# Pega o backup mais recente (antes da quebra)
backup = max(backups, key=os.path.getctime)
print(f"[OK] Restaurando do backup: {backup}")
shutil.copy2(backup, arq)
print("[OK] Template restaurado ao estado anterior (com BP preenchido).")

# Salva o template quebrado atual como referência
shutil.copy2(arq, f"pc_frontend\\relatorio_consolidado_template_QUEBRADO_REFERENCIA.html")
