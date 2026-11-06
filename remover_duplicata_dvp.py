import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. No HTML: remove a segunda ocorrência de "Análise Patrimonial" (a duplicata)
    # Encontra todas as tags <a> que contém "Análise Patrimonial"
    padrao_patrimonial = re.compile(
        r'<li><a[^>]*href="/analise_patrimonial"[^>]*>.*?</a></li>\s*',
        re.DOTALL
    )
    ocorrencias = list(padrao_patrimonial.finditer(c))
    
    if len(ocorrencias) > 1:
        # Remove todas, menos a primeira
        for match in ocorrencias[1:]:
            c = c[:match.start()] + c[match.end():]
        print(f"[OK] {arq} - Duplicata de Analise Patrimonial removida do HTML.")

    # 2. No JavaScript: remove a duplicata da lista linksParaMover (se houver)
    padrao_links = re.compile(
        r"const linksParaMover = \[(.*?)\];",
        re.DOTALL
    )
    match = padrao_links.search(c)
    if match:
        lista_atual = match.group(1)
        # Remove duplicatas de "Análise Patrimonial"
        itens = re.findall(r"'([^']+)'", lista_atual)
        vistos = set()
        itens_unicos = []
        for item in itens:
            if item not in vistos:
                vistos.add(item)
                itens_unicos.append(item)
        
        if len(itens_unicos) < len(itens):
            nova_lista = ", ".join([f"'{i}'" for i in itens_unicos])
            c = c[:match.start()] + "const linksParaMover = [" + nova_lista + "];" + c[match.end():]
            print(f"[OK] {arq} - Duplicata removida da lista linksParaMover.")

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_remove_dup_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Alteracoes salvas.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
