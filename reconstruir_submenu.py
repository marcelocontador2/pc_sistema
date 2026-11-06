import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. Substitui a lista linksParaMover por uma lista limpa
    padrao_links = re.compile(
        r"const linksParaMover = \[(.*?)\];",
        re.DOTALL
    )
    match = padrao_links.search(c)
    if match:
        lista_limpa = """[
        'Conferência das Demonstrações',
        'Integridade entre Demonstrações',
        'Análise Orçamentária (BO)',
        'Análise Financeira (BF)',
        'Análise DFC',
        'Análise Patrimonial (DVP)',
        'Composição Receitas/Despesas',
        'Índices de Liquidez',
        'Resultados Gerais'
    ]"""
        c = c[:match.start()] + "const linksParaMover = " + lista_limpa + ";" + c[match.end():]
        print(f"[OK] {arq} - Lista linksParaMover substituida por lista limpa.")

    # 2. Remove scripts duplicados que adicionam "Análise DFC" e "Análise Orçamentária" dinamicamente
    # (para evitar duplicatas)
    padrao_dup_dfc = re.compile(
        r"// Verifica se o item já existe para não duplicar\s*\n\s*if \(!submenuAnalises\.textContent\.includes\('Análise DFC'\)\) \{.*?\n\s*\}\s*\n",
        re.DOTALL
    )
    c = padrao_dup_dfc.sub('', c)
    
    padrao_dup_orc = re.compile(
        r"// Verifica se o item já existe para não duplicar\s*\n\s*if \(!submenuAnalises\.textContent\.includes\('Análise Orçamentária \(BO\)'\)\) \{.*?\n\s*\}\s*\n",
        re.DOTALL
    )
    c = padrao_dup_orc.sub('', c)

    print(f"[OK] {arq} - Scripts duplicados de DFC e Orcamentaria removidos.")

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_reconstruir_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Alteracoes salvas.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
