import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. Encontra o bloco <li> que contém "Análise Orçamentária" (o início do bloco de análises)
    idx_orc = c.find('Análise Orçamentária')
    if idx_orc == -1:
        print(f"[AVISO] {arq}: nao encontrei 'Análise Orçamentária'.")
        continue

    # 2. Encontra o início do <li> (antes de "Análise Orçamentária")
    start_li = c.rfind('<li', 0, idx_orc)
    if start_li == -1:
        print(f"[AVISO] {arq}: nao encontrei o <li> que abrange a Analise Orcamentaria.")
        continue

    # 3. Encontra o fechamento do </li> (depois de "Análise Patrimonial")
    idx_pat = c.find('Análise Patrimonial', idx_orc)
    if idx_pat == -1:
        print(f"[AVISO] {arq}: nao encontrei 'Análise Patrimonial'.")
        continue

    end_li = c.find('</li>', idx_pat) + 5
    if end_li == -1:
        print(f"[AVISO] {arq}: nao encontrei o </li> da Analise Patrimonial.")
        continue

    # 4. Substitui TODO o bloco <li>...</li> por um novo, limpo
    bloco_novo = '''<li>
        <a href="/analise_orcamentaria" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise Orçamentária (BO)</a>
        <a href="/analise_financeira_bf" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise Financeira (BF)</a>
        <a href="/analise_dfc" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise DFC</a>
        <a href="/analise_patrimonial" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise Patrimonial (DVP)</a>
    </li>'''

    c = c[:start_li] + bloco_novo + c[end_li:]

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_li_correto_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Bloco de analises substituido (BO, BF, DFC, DVP).")
    else:
        print(f"[AVISO] {arq} - Nenhuma alteracao necessaria.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
