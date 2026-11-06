import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. Adiciona o link no HTML estatico (se nao existir)
    if 'href="/analise_bp"' not in c:
        idx_bf = c.find('href="/analise_financeira_bf"')
        if idx_bf != -1:
            fim_bf = c.find('</a>', idx_bf) + 4
            if fim_bf != -1:
                link_bp = '\n            <a href="/analise_bp" style="text-decoration:none; color:inherit;" class="menu-item">Análise BP</a>'
                c = c[:fim_bf] + link_bp + c[fim_bf:]
                print(f"[OK] {arq} - Link 'Análise BP' adicionado.")

    # 2. Adiciona o item na lista linksParaMover (se nao existir)
    if "'Análise BP'" not in c:
        padrao = re.compile(r"(const linksParaMover = \[)(.*?)(\];)", re.DOTALL)
        match = padrao.search(c)
        if match:
            lista_atual = match.group(2)
            lista_nova = lista_atual.rstrip() + ",\n        'Análise BP'"
            c = c[:match.start(2)] + lista_nova + c[match.end(2):]
            print(f"[OK] {arq} - 'Análise BP' adicionada à lista linksParaMover.")

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_add_bp_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Alteracoes salvas.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
