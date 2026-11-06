import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. Remove a duplicata do HTML (as que estão com class="menu-item")
    padrao_dup_html = re.compile(
        r'\s*<a href="/analise_patrimonial"[^>]*class="menu-item"[^>]*>Análise Patrimonial</a>',
        re.DOTALL
    )
    c = padrao_dup_html.sub('', c)
    print(f"[OK] {arq} - Duplicatas de 'menu-item' removidas do HTML.")

    # 2. Remove a duplicata do JavaScript (textContent = 'Análise Patrimonial (DVP)')
    # Procura o bloco que adiciona essa entrada e remove
    padrao_js_dup = re.compile(
        r"// Verifica se o item já existe para não duplicar\s*\n\s*if \(!submenuAnalises\.textContent\.includes\('Análise Patrimonial \(DVP\)'\)\) \{.*?\n\s*\}\s*\n",
        re.DOTALL
    )
    c = padrao_js_dup.sub('', c)
    print(f"[OK] {arq} - Script que duplicava 'Análise Patrimonial (DVP)' removido.")

    # 3. Verifica se o array linksParaMover ainda tem a DVP duplicada
    # (aqui não precisa mexer, pois a lista está ok)

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_remove_dup_dvp_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Alteracoes salvas.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
