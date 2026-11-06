import glob, os, shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
alterados = 0

for arq in glob.glob("pc_frontend/*.html"):
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    # Se ja tem o link, pula
    if 'href="/analise_dfc"' in c:
        continue

    # Procura o link do BF (se existir) para inserir ao lado
    # Se nao existir, procura "Análises Contábeis" ou insere antes de </ul> do menu
    
    # Caso 1: existe link para analise_financeira_bf
    idx_bf = c.find('href="/analise_financeira_bf"')
    if idx_bf != -1:
        # Pega a linha inteira <li>...</li> do BF
        start_li = c.rfind("<li>", 0, idx_bf)
        end_li = c.find("</li>", idx_bf) + 5
        if start_li != -1 and end_li != -1:
            li_bf = c[start_li:end_li]
            # Cria uma versao adaptada para DFC
            li_dfc = li_bf.replace("/analise_financeira_bf", "/analise_dfc").replace("Análise Financeira-BF", "Análise DFC").replace("Análise BF", "Análise DFC")
            if 'href="/analise_dfc"' not in li_dfc:
                li_dfc = li_dfc.replace("href=", 'href="/analise_dfc" data-old-href=', 1)
            
            c = c[:end_li] + "\n" + li_dfc + c[end_li:]
            shutil.copy2(arq, f"{arq}.bak_dfc_{ts}")
            open(arq, "w", encoding="utf-8").write(c)
            alterados += 1
            print(f"[OK] {arq} - link DFC adicionado ao lado do BF")
            continue

    # Caso 2: existe "Análises Contábeis" (menu principal)
    idx_ac = c.find("Análises Contábeis")
    if idx_ac != -1:
        # Insere um novo <li> antes do </ul> do menu, se possivel
        # Mas o mais seguro e colocar dentro do submenu, se existir
        pass

print(f"\n[OK] {alterados} arquivos alterados.")
