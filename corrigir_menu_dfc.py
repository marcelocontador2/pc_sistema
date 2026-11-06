import glob, os, shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
alterados = 0

for arq in glob.glob("pc_frontend/*.html"):
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    if 'analise_dfc' not in c:
        continue

    c_original = c

    # 1. Remove QUALQUER link da DFC que ja exista (para nao duplicar)
    # O link foi inserido como <a href="/analise_dfc" ...>Análise DFC</a>
    c = re.sub(r'\s*<a\s+href="/analise_dfc"[^>]*>Análise DFC</a>', '', c)

    # 2. Insere o link da DFC LOGO APOS o link do BF (se existir)
    idx_bf = c.find('href="/analise_financeira_bf"')
    if idx_bf != -1:
        # Acha o fim da tag </a> do BF
        fim_bf = c.find('</a>', idx_bf) + 4
        if fim_bf != -1:
            # Monta o link da DFC com o mesmo estilo do BF
            li_dfc = '\n        <a href="/analise_dfc" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Análise DFC</a>'
            c = c[:fim_bf] + li_dfc + c[fim_bf:]
            print(f"[OK] {arq} - link DFC inserido apos o BF.")
        else:
            print(f"[AVISO] {arq} - nao encontrei o fechamento </a> do BF.")
    else:
        # Se nao existe BF, insere apos "Análise Patrimonial" se existir
        idx_pat = c.find('Análise Patrimonial')
        if idx_pat != -1:
            fim_pat = c.find('</a>', idx_pat) + 4
            li_dfc = '\n        <a href="/analise_dfc" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Análise DFC</a>'
            c = c[:fim_pat] + li_dfc + c[fim_pat:]
            print(f"[OK] {arq} - link DFC inserido apos Analise Patrimonial.")

    if c != c_original:
        shutil.copy2(arq, f"{arq}.bak_dfc_fix_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        alterados += 1

print(f"\n[OK] {alterados} arquivos ajustados.")
