import glob, os, shutil

# Busca todos os backups do index.html na pasta frontend
backups = glob.glob(r"pc_frontend\index_backup_*.html")

if not backups:
    print("[ERRO CRÍTICO] Nenhum backup encontrado!")
    exit()

# Ordena do mais antigo para o mais novo
backups.sort(key=os.path.getctime)

# Pega o backup MAIS ANTIGO da lista (que é o estado original antes de todas as mexidas de hoje)
backup_original = backups[0]

print(f"Restaurando o arquivo original: {backup_original}")
shutil.copy2(backup_original, r"pc_frontend\index.html")

print("[OK] O arquivo index.html foi restaurado para o estado original, antes de qualquer alteração no menu hoje.")
