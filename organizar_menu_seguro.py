import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # Substitui a lista linksParaMover pela ordem exata que voce pediu
    padrao = re.compile(r"(const linksParaMover = \[)(.*?)(\];)", re.DOTALL)
    match = padrao.search(c)
    if match:
        lista_nova = """[
        'Conferência das Demonstrações',
        'Integridade entre Demonstrações',
        'Análise BP',
        'Análise Orçamentária (BO)',
        'Análise Financeira (BF)',
        'Análise DFC',
        'Análise Patrimonial (DVP)',
        'Índices de Liquidez',
        'Composição Receitas/Despesas',
        'Resultados Gerais',
        'Comparativo de Receitas',
        'Comparativo de Despesas',
        'Análise por Centro de Custos',
        'Custo de Pessoal'
    ]"""
        c = c[:match.start(2)] + lista_nova + c[match.end(2):]
        print(f"[OK] {arq} - Lista linksParaMover reorganizada.")

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_ordem_menu_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Alteracoes salvas.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
