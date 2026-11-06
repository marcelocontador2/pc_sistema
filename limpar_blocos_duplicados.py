import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. Remove o BLOCO 2 (Análise Orçamentária + Financeira-BF + DFC sem acentos)
    padrao_bloco2 = re.compile(
        r'<a href="/analise_orcamentaria"[^>]*>Análise Orçamentária</a>.*?<a href="/analise_financeira_bf"[^>]*>Análise Financeira-BF</a>.*?<a href="/analise_dfc"[^>]*>Análise DFC</a>\s*',
        re.DOTALL
    )
    c = padrao_bloco2.sub('', c)

    # 2. Remove o BLOCO 3 (Análise Orçamentária sozinho)
    padrao_bloco3 = re.compile(
        r'<a href="/analise_orcamentaria"[^>]*>Análise Orçamentária</a>\s*',
        re.DOTALL
    )
    c = padrao_bloco3.sub('', c)

    # 3. Remove qualquer DFC duplicado que sobrar (fora do bloco correto)
    # Procura DFC que não esteja entre Conferência e Integridade
    # (mais simples: remove todos os <a href="/analise_dfc"> e recoloca só se necessário)
    # Vamos deixar o script JS fazer o trabalho de mover para o submenu

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_limpeza_final_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Blocos duplicados (sem acentos) removidos.")
    else:
        print(f"[AVISO] {arq} - Nenhuma alteracao necessaria.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
