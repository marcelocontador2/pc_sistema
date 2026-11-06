import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. Procura a lista de links que sao movidos para o submenu (linksParaMover)
    # e adiciona o DFC. Tambem remove a duplicata de Analise Patrimonial.
    padrao_links = re.compile(
        r"const linksParaMover = \[(.*?)\];",
        re.DOTALL
    )
    match = padrao_links.search(c)
    if match:
        # Pega o conteúdo atual da lista
        lista_atual = match.group(1)
        
        # Remove duplicatas de 'Análise Patrimonial' (mantém apenas uma)
        lista_atual = re.sub(r"(['\"]Análise Patrimonial['\"],?\s*){2,}", r"\1", lista_atual)
        
        # Adiciona a Análise DFC se não existir
        if "Análise DFC" not in lista_atual:
            lista_atual = lista_atual.rstrip() + ", 'Análise DFC'"
        
        # Substitui no HTML
        c = c[:match.start()] + "const linksParaMover = [" + lista_atual + "];" + c[match.end():]
        print(f"[OK] {arq} - Lista de links movidos atualizada (DFC adicionado, DVP sem duplicata).")
    else:
        print(f"[AVISO] {arq} - Nao encontrei 'linksParaMover'.")

    # 2. Se houver um array de links movidos dentro do JavaScript, podemos ajustar
    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_links_mover_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Alteracoes salvas.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
