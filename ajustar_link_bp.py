import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. Ajusta o estilo do link 'Análise BP' para ficar igual aos outros
    antigo = '<a href="/analise_bp" style="text-decoration:none; color:inherit;" class="menu-item">Análise BP</a>'
    novo = '<a href="/analise_bp" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise BP</a>'
    
    if antigo in c:
        c = c.replace(antigo, novo, 1)
        print(f"[OK] {arq} - Estilo do link 'Análise BP' ajustado.")

    # 2. Adiciona 'Análise BP' na lista linksParaMover (se não existir)
    if "'Análise BP'" not in c:
        padrao = re.compile(r"(const linksParaMover = \[)(.*?)(\];)", re.DOTALL)
        match = padrao.search(c)
        if match:
            lista_atual = match.group(2)
            lista_nova = lista_atual.rstrip() + ",\n        'Análise BP'"
            c = c[:match.start(2)] + lista_nova + c[match.end(2):]
            print(f"[OK] {arq} - 'Análise BP' adicionada à lista linksParaMover.")

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_ajuste_bp_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Alteracoes salvas.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
