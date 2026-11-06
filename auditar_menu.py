import os, re

print("=== PROCURANDO ARQUIVOS DE MENU/INDEX ===")
# Procura arquivos html na pasta frontend que tenham a palavra "Análises Contábeis" ou "menu"
for root, dirs, files in os.walk("pc_frontend"):
    for nome in files:
        if nome.endswith(".html"):
            caminho = os.path.join(root, nome)
            with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
                if "Análises Contábeis" in txt or "menu" in txt.lower() and "href" in txt:
                    print(f"\n>>> Encontrado em: {caminho}")
                    # Mostra o trecho do menu (procurando 'Análises Contábeis')
                    idx = txt.find("Análises Contábeis")
                    if idx == -1:
                        idx = txt.find("Análises")
                    if idx != -1:
                        print(txt[max(0, idx-500):idx+1000])
                    else:
                        print("(Menu não encontrado no texto)")
                    break
