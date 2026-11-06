import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
alterados = 0

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    # Remove qualquer link antigo do DFC
    c = c.replace('<a href="/analise_dfc" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Análise DFC</a>', '')

    # Encontra a tag exata do BF
    tag_bf = '<a href="/analise_financeira_bf" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Análise Financeira-BF</a>'
    
    if tag_bf in c:
        # Cria a tag do DFC logo abaixo
        tag_dfc = '\n        <a href="/analise_dfc" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Análise DFC</a>'
        
        # Substitui a tag do BF por ela mesma + o DFC
        c = c.replace(tag_bf, tag_bf + tag_dfc, 1)
        
        shutil.copy2(arq, f"{arq}.bak_dfc_certeza_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        alterados += 1
        print(f"[OK] {arq} - link 'Análise DFC' inserido logo apos o BF.")
    else:
        print(f"[AVISO] {arq} - nao encontrei a tag exata do BF.")

print(f"\n[OK] {alterados} arquivos alterados.")
