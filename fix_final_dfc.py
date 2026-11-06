import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
alterados = 0

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    # 1. Remove o link do DFC que esta no lugar errado
    c = c.replace('href="/analise_dfc" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Análise DFC</a>', '')
    
    # 2. Restaura o BF (que foi trocado)
    if 'href="/analise_financeira_bf"' not in c:
        c = c.replace(
            'href="/analise_orcamentaria" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Análise Orçamentária</a>',
            'href="/analise_orcamentaria" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Análise Orçamentária</a>\n        <a href="/analise_financeira_bf" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Análise Financeira-BF</a>'
        )

    # 3. Agora adiciona o DFC DEPOIS do BF, mantendo a estrutura do <li>
    idx_bf = c.find('href="/analise_financeira_bf"')
    if idx_bf != -1:
        end_a_bf = c.find('</a>', idx_bf) + 4
        # Insere o DFC logo apos o fechamento do BF
        li_dfc = '\n        <a href="/analise_dfc" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Análise DFC</a>'
        c = c[:end_a_bf] + li_dfc + c[end_a_bf:]

    shutil.copy2(arq, f"{arq}.bak_fix_final_dfc_{ts}")
    open(arq, "w", encoding="utf-8").write(c)
    alterados += 1
    print(f"[OK] {arq} - links do BF e DFC corrigidos.")

print(f"\n[OK] {alterados} arquivos alterados.")
