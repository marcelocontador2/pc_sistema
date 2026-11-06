import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
alterados = 0

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    # Verifica se o link do DFC ja esta no HTML (para nao duplicar)
    if 'href="/analise_dfc"' in c:
        print(f"[AVISO] {arq} ja tem link para analise_dfc.")
        continue

    # Onde o menu do BF esta
    idx_bf = c.find('href="/analise_financeira_bf"')
    if idx_bf == -1:
        print(f"[AVISO] {arq} nao tem o link do BF.")
        continue

    # Encontra o fim da tag <a> ou <li> do BF
    end_tag = c.find('</a>', idx_bf)
    if end_tag == -1:
        end_tag = c.find('</li>', idx_bf)
        
    if end_tag != -1:
        # Vamos extrair o estilo exato do BF para usar no DFC
        # Pega a tag <a> do BF inteira
        start_a = c.rfind('<a', 0, idx_bf)
        end_a = c.find('</a>', idx_bf) + 4
        tag_bf = c[start_a:end_a]
        
        # Cria a tag do DFC substituindo o href e o texto
        tag_dfc = tag_bf.replace('/analise_financeira_bf', '/analise_dfc').replace('Análise Financeira-BF', 'Análise DFC').replace('Análise Financeira (BF)', 'Análise DFC')
        
        # Adiciona no final do <li> do BF
        end_li = c.find('</li>', idx_bf)
        if end_li == -1:
            # Se nao tiver <li>, insere logo apos o </a>
            end_li = end_a
            
        if end_li != -1:
            c = c[:end_li] + '\n        ' + tag_dfc + c[end_li:]
            
            shutil.copy2(arq, f"{arq}.bak_dfc_correto_{ts}")
            open(arq, "w", encoding="utf-8").write(c)
            alterados += 1
            print(f"[OK] {arq} - link 'Análise DFC' adicionado dentro do submenu.")

print(f"\n[OK] {alterados} arquivos alterados.")
