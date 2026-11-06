import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. Encontra o bloco de links de analise no HTML
    # (do primeiro <a> de "Conferência" ate o ultimo <a> de "Custo de Pessoal")
    idx_conf = c.find('Conferência das Demonstrações')
    if idx_conf == -1:
        print(f"[AVISO] {arq} - Nao encontrei 'Conferência das Demonstrações'.")
        continue

    start_a = c.rfind('<a', 0, idx_conf)
    if start_a == -1:
        start_a = idx_conf

    # Encontra o fim do bloco (depois do "Custo de Pessoal")
    idx_fim = c.find('Custo de Pessoal', idx_conf)
    if idx_fim == -1:
        print(f"[AVISO] {arq} - Nao encontrei 'Custo de Pessoal'.")
        continue

    end_a = c.find('</a>', idx_fim) + 4
    if end_a == -1:
        end_a = idx_fim + 100

    # 2. Extrai os links existentes
    bloco_antigo = c[start_a:end_a]
    links = re.findall(r'<a[^>]*>.*?</a>', bloco_antigo, re.DOTALL)
    print(f"[INFO] {arq} - {len(links)} links encontrados no bloco.")

    # 3. Cria um dicionario de links por texto (usando o texto visivel)
    links_por_texto = {}
    for link in links:
        texto = re.sub(r'<[^>]+>', '', link).strip()
        links_por_texto[texto] = link
        print(f"  Texto: '{texto}'")

    # 4. Ordem desejada
    ordem = [
        'Conferência das Demonstrações',
        'Integridade entre Demonstrações',
        'Análise BP',
        'Análise Orçamentária (BO)',
        'Análise Financeira (BF)',
        'Análise DFC',
        'Análise Patrimonial (DVP)',
        'Índices de Liquidez',
        'Composição Receitas/Despesas',
        'Resultados Gerais',
        'Comparativo de Receitas',
        'Comparativo de Despesas',
        'Análise por Centro de Custos',
        'Custo de Pessoal'
    ]

    # 5. Monta o bloco novo na ordem correta
    bloco_novo = ''
    for texto in ordem:
        if texto in links_por_texto:
            bloco_novo += links_por_texto[texto] + '\n            '
            print(f"  [OK] '{texto}' adicionado na ordem.")
        else:
            print(f"  [AVISO] '{texto}' nao encontrado no bloco.")

    # 6. Substitui o bloco antigo pelo novo
    if bloco_novo:
        c = c[:start_a] + bloco_novo + c[end_a:]
        shutil.copy2(arq, f"{arq}.bak_ordem_html_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Bloco de links reorganizado (mantendo o HTML ao redor).")
    else:
        print(f"[AVISO] {arq} - Nenhum link foi reorganizado.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
