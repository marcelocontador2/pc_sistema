import glob, shutil, os

# Encontra os arquivos do relatório
arquivos_alvo = glob.glob(r"pc_frontend\relatorio_comparativo_receitas_v2.html") + \
                glob.glob(r"pc_frontend\relatorio_comparativo_receitas.html")

if not arquivos_alvo:
    print("[ERRO] Nenhum arquivo de relatório de receitas encontrado.")
else:
    for arquivo in arquivos_alvo:
        # Busca o backup mais recente feito pelo último script
        backups = sorted(glob.glob(f"{arquivo}.bak_pag_final_*"), reverse=True)
        
        if backups:
            backup_recente = backups[0]
            shutil.copy2(backup_recente, arquivo)
            print(f"[OK] Restaurado: {os.path.basename(arquivo)}")
            print(f"     A partir do backup: {os.path.basename(backup_recente)}")
        else:
            print(f"[AVISO] Nenhum backup .bak_pag_final_ encontrado para {os.path.basename(arquivo)}")
            # Tenta um backup anterior (do script de correção de paginação)
            backups_antigos = sorted(glob.glob(f"{arquivo}.bak_paginacao_*"), reverse=True)
            if backups_antigos:
                shutil.copy2(backups_antigos[0], arquivo)
                print(f"[OK] Restaurado do backup anterior: {os.path.basename(backups_antigos[0])}")

print()
print("O arquivo foi revertido para o estado anterior à tentativa de compactação.")
