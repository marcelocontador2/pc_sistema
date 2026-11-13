import shutil
import os

path = "analise_dmpl.html"
backup = path + ".bak_exibir_dmpl" # O backup que fizemos antes da ultima alteracao

if not os.path.exists(backup):
    print("ERRO: Backup nao encontrado!")
else:
    # Restaura o backup (que tem o HTML original antes da ultima bagunça)
    shutil.copy(backup, path)
    print("OK: Arquivo restaurado para a versao anterior (antes da ultima alteracao).")
    
    # Agora vamos ler o arquivo restaurado e ver como esta a funcao exibirSelecionado
    with open(path, "r", encoding="utf-8") as f:
        s = f.read()
        
    # Apenas verifica se a funcao voltou a ser como era
    import re
    match = re.search(r'function exibirSelecionado\(\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
    if match:
        print("\n=== FUNCAO RESTAURADA (PRIMEIRAS LINHAS) ===")
        print(match.group(0)[:300])
