import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
alterados = 0

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. REMOVE todos os <li> que contenham "Análise Orçamentária", "Análise Financeira", "Análise DFC" ou "Análise Patrimonial"
    # Vamos usar regex para pegar o bloco <li>...</li> completo
    padrao = re.compile(
        r'<li>\s*<a[^>]*>(?:Análise Orçamentária|Análise Financeira[^<]*|Análise DFC|Análise Patrimonial)</a>.*?</li>',
        re.DOTALL
    )
    c = padrao.sub('', c)

    # 2. Também remove as tags <a> soltas que ficaram fora de <li>
    c = re.sub(r'<a\s+href="/analise_orcamentaria"[^>]*>Análise Orçamentária</a>', '', c)
    c = re.sub(r'<a\s+href="/analise_financeira_bf"[^>]*>Análise Financeira[^<]*</a>', '', c)
    c = re.sub(r'<a\s+href="/analise_dfc"[^>]*>Análise DFC</a>', '', c)
    c = re.sub(r'<a\s+href="/analise_patrimonial"[^>]*>Análise Patrimonial</a>', '', c)

    # 3. Insere o bloco limpo logo após o link do "Relatorio Consolidado"
    idx = c.find('Relatorio Consolidado')
    if idx != -1:
        # Encontra o fechamento do <li> do Relatorio Consolidado
        end_li = c.find('</li>', idx) + 5
        if end_li != -1:
            bloco_limpo = '''
    <li><a href="/analise_orcamentaria" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Análise Orçamentária</a></li>
    <li><a href="/analise_financeira_bf" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Análise Financeira-BF</a></li>
    <li><a href="/analise_dfc" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Análise DFC</a></li>
    <li><a href="/analise_patrimonial" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Análise Patrimonial</a></li>'''
            c = c[:end_li] + bloco_limpo + c[end_li:]

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_limpeza_ana_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        alterados += 1
        print(f"[OK] {arq} - Menu de Análises limpo e reorganizado.")

print(f"\n[OK] {alterados} arquivos alterados.")
