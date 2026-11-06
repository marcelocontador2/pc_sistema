import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. Remove TODAS as linhas que contenham "Análise Patrimonial" (para eliminar duplicatas e o original)
    c = re.sub(r'<li><a href="/analise_patrimonial"[^>]*>.*?</a></li>\s*', '', c)
    
    # 2. Remove TODAS as linhas que contenham "Análise Orçamentária" (para eliminar duplicatas e o original)
    c = re.sub(r'<li><a href="/analise_orcamentaria"[^>]*>.*?</a></li>\s*', '', c)
    
    # 3. Remove TODAS as linhas que contenham "Análise Financeira" (para eliminar duplicatas e o original)
    c = re.sub(r'<li><a href="/analise_financeira_bf"[^>]*>.*?</a></li>\s*', '', c)
    
    # 4. Remove TODAS as linhas que contenham "Análise DFC" (para eliminar duplicatas e o original)
    c = re.sub(r'<li><a href="/analise_dfc"[^>]*>.*?</a></li>\s*', '', c)

    # 5. Encontra o link da Conferência das Demonstrações e insere os 4 links corretos depois dele
    idx_conf = c.find('href="/conferencia"')
    if idx_conf != -1:
        # Encontra o fechamento do <li> da Conferência
        fim_li_conf = c.find('</li>', idx_conf) + 5
        
        if fim_li_conf != -1:
            # Bloco limpo com os 4 links na ordem correta
            bloco_correto = '''
        <li><a href="/analise_orcamentaria" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise Orçamentária (BO)</a></li>
        <li><a href="/analise_financeira_bf" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise Financeira (BF)</a></li>
        <li><a href="/analise_dfc" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise DFC</a></li>
        <li><a href="/analise_patrimonial" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise Patrimonial (DVP)</a></li>
'''
            c = c[:fim_li_conf] + bloco_correto + c[fim_li_conf:]
        else:
            print(f"[AVISO] {arq}: nao encontrei o fim do <li> da Conferencia.")
    else:
        print(f"[AVISO] {arq}: nao encontrei o link da Conferencia.")

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_final_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Duplicatas removidas e bloco corrigido (BO, BF, DFC, DVP).")
    else:
        print(f"[AVISO] {arq} - Nenhuma alteracao necessaria.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
