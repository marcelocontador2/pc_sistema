import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    # Encontra todas as ocorrências de "Análise Patrimonial (DVP)"
    termo = 'Análise Patrimonial (DVP)'
    ocorrencias = []
    pos = 0
    while True:
        pos = c.find(termo, pos)
        if pos == -1:
            break
        ocorrencias.append(pos)
        pos += 1

    print(f"[INFO] {arq}: {len(ocorrencias)} ocorrências de 'Análise Patrimonial (DVP)'.")

    if len(ocorrencias) >= 2:
        # Pega a SEGUNDA ocorrência (a duplicata)
        pos_dup = ocorrencias[1]

        # Encontra o <a> que contém essa ocorrência (do início da tag até o fechamento)
        start_a = c.rfind('<a', 0, pos_dup)
        end_a = c.find('</a>', pos_dup) + 4

        if start_a != -1 and end_a != -1:
            tag_antiga = c[start_a:end_a]
            # Substitui a tag duplicada por uma tag da Análise DFC
            tag_nova = tag_antiga.replace('Análise Patrimonial (DVP)', 'Análise DFC')
            tag_nova = tag_nova.replace('/analise_patrimonial', '/analise_dfc')

            c = c[:start_a] + tag_nova + c[end_a:]

            shutil.copy2(arq, f"{arq}.bak_dvp_dfc_{ts}")
            open(arq, "w", encoding="utf-8").write(c)
            print(f"[OK] {arq}: duplicata de DVP removida e DFC inserida.")
        else:
            print(f"[AVISO] {arq}: nao encontrei a tag <a> da duplicata.")
    elif len(ocorrencias) == 1:
        # Se so tem uma DVP, insere o DFC logo depois
        pos = ocorrencias[0]
        end_a = c.find('</a>', pos) + 4
        if end_a != -1:
            tag_dfc = '\n        <a href="/analise_dfc" style="display:block; padding:8px 0px 8px 15px; text-decoration:none; color:#555;">Análise DFC</a>'
            c = c[:end_a] + tag_dfc + c[end_a:]
            shutil.copy2(arq, f"{arq}.bak_dvp_dfc_{ts}")
            open(arq, "w", encoding="utf-8").write(c)
            print(f"[OK] {arq}: DFC inserida apos a DVP unica.")
    else:
        print(f"[AVISO] {arq}: nenhuma ocorrencia de 'Analise Patrimonial' encontrada.")

print("\n[OK] Pronto. Teste no navegador com Ctrl+Shift+R.")
