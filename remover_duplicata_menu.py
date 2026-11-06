import re, shutil, datetime

arquivo = r"pc_frontend\index.html"
backup = f"pc_frontend\\index_backup_dup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# Encontra todas as ocorrências do texto "Análises Contábeis"
ocorrencias = [m.start() for m in re.finditer('Análises Contábeis', html)]

if len(ocorrencias) >= 2:
    # A primeira ocorrência é a tag solta (a que está duplicada)
    # A segunda ocorrência é a tag dentro do <ul> com os itens corretos.
    
    # Para remover a primeira, precisamos apagar o <li> que a envolve.
    idx_dup = ocorrencias[0]
    start_li = html.rfind('<li', 0, idx_dup)
    end_li = html.find('</li>', idx_dup) + 5
    
    if start_li != -1 and end_li != -1:
        # Remove o bloco duplicado
        html = html[:start_li] + html[end_li:]
        
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(html)
        print("[OK] Tag 'Análises Contábeis' duplicada removida com sucesso.")
    else:
        print("[AVISO] Não encontrei os limites do <li> duplicado.")
else:
    print("[INFO] Não há duplicatas de 'Análises Contábeis'.")
