import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
alterados = 0

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    # 1. Remove qualquer link antigo do DFC (para nao duplicar)
    c = re.sub(r'\s*<li><a href="/analise_dfc"[^>]*>.*?</a></li>', '', c)
    c = re.sub(r'\s*<a href="/analise_dfc"[^>]*>.*?</a>', '', c)

    # 2. Encontra o link do BF
    idx_bf = c.find('href="/analise_financeira_bf"')
    if idx_bf == -1:
        print(f"[AVISO] {arq} nao tem o link do BF.")
        continue

    # Pega o <li> inteiro do BF (do <li> ate o </li>)
    start_li = c.rfind('<li>', 0, idx_bf)
    end_li = c.find('</li>', idx_bf) + 5
    
    if start_li == -1 or end_li == -1:
        print(f"[AVISO] {arq} - nao encontrei o bloco <li> completo do BF.")
        continue

    tag_li_bf = c[start_li:end_li]

    # Cria a tag do DFC baseada no <li> do BF
    tag_li_dfc = tag_li_bf.replace('/analise_financeira_bf', '/analise_dfc')
    tag_li_dfc = tag_li_dfc.replace('Análise Financeira-BF', 'Análise DFC')
    tag_li_dfc = tag_li_dfc.replace('Análise Financeira (BF)', 'Análise DFC')

    # Insere o <li> do DFC logo apos o <li> do BF
    c = c[:end_li] + '\n        ' + tag_li_dfc + c[end_li:]

    shutil.copy2(arq, f"{arq}.bak_submenu_dfc_{ts}")
    open(arq, "w", encoding="utf-8").write(c)
    alterados += 1
    print(f"[OK] {arq} - link 'Análise DFC' inserido no submenu.")

print(f"\n[OK] {alterados} arquivos alterados.")
