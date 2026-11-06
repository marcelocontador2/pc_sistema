import os, glob, shutil

# Busca todos os backups do arquivo de receitas
backups = glob.glob(r"pc_frontend\analise_comparativo_receitas.html.bak_*")

if not backups:
    print("[ERRO] Nenhum backup do arquivo de receitas encontrado.")
else:
    # Pega o backup mais recente (feito antes de estragar)
    backup_mais_recente = max(backups, key=os.path.getctime)
    print(f"Restaurando o arquivo do backup: {backup_mais_recente}")
    
    # Copia o backup de volta para o arquivo original
    shutil.copy2(backup_mais_recente, r"pc_frontend\analise_comparativo_receitas.html")
    print("[OK] O arquivo analise_comparativo_receitas.html foi restaurado com sucesso.")
    print("[OK] O layout e o botão de excluir original devem voltar a funcionar.")

# Faz o mesmo para o arquivo de despesas
backups_desp = glob.glob(r"pc_frontend\analise_comparativo_despesas.html.bak_*")
if backups_desp:
    backup_desp = max(backups_desp, key=os.path.getctime)
    print(f"Restaurando o arquivo do backup: {backup_desp}")
    shutil.copy2(backup_desp, r"pc_frontend\analise_comparativo_despesas.html")
    print("[OK] O arquivo analise_comparativo_despesas.html foi restaurado com sucesso.")
else:
    print("[INFO] Nenhum backup de despesas encontrado. Nada foi alterado.")
