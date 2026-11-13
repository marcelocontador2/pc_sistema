import os
import re
import shutil

arquivos = ["custo_pessoal_pdf_resumo.html", "custo_pessoal_pdf_completo.html"]

for arquivo in arquivos:
    if not os.path.exists(arquivo):
        print(f"AVISO: Arquivo {arquivo} não encontrado.")
        continue
    
    with open(arquivo, "r", encoding="utf-8") as f:
        s = f.read()
    
    shutil.copy(arquivo, arquivo + ".bak_charset")
    
    # Verifica se já tem meta charset
    if 'charset="utf-8"' in s.lower() or "charset='utf-8'" in s.lower() or 'charset=utf-8' in s.lower():
        print(f"OK: {arquivo} já possui a meta charset UTF-8.")
    else:
        # Procura a tag <head> e injeta o meta logo após
        if "<head>" in s:
            s = s.replace("<head>", '<head>\n    <meta charset="UTF-8">', 1)
            with open(arquivo, "w", encoding="utf-8") as f:
                f.write(s)
            print(f"OK: Meta charset UTF-8 adicionada em {arquivo}.")
        else:
            # Se não tiver <head>, coloca no topo do arquivo
            s = '<meta charset="UTF-8">\n' + s
            with open(arquivo, "w", encoding="utf-8") as f:
                f.write(s)
            print(f"OK: Meta charset UTF-8 adicionada no topo de {arquivo} (sem tag <head>).")

print("\nPROCESSO CONCLUIDO!")
