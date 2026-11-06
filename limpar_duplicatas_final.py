import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
alterados = 0

# Lista oficial e limpa de links
links_oficiais = """
                <li style="margin-bottom: 8px;"><a href="/conferencia" style="text-decoration: none; color: #555;">Conferência das Demonstrações</a></li>
                <li style="margin-bottom: 8px;"><a href="/integridade" style="text-decoration: none; color: #555;">Integridade entre Demonstrações</a></li>
                <li style="margin-bottom: 8px;"><a href="/analise_orcamentaria" style="text-decoration: none; color: #555;">Análise Orçamentária (BO)</a></li>
                <li style="margin-bottom: 8px;"><a href="/analise_financeira_bf" style="text-decoration: none; color: #555;">Análise Financeira (BF)</a></li>
                <li style="margin-bottom: 8px;"><a href="/analise_dfc" style="text-decoration: none; color: #555;">Análise DFC</a></li>
                <li style="margin-bottom: 8px;"><a href="/analise_patrimonial" style="text-decoration: none; color: #555;">Análise Patrimonial (DVP)</a></li>
                <li style="margin-bottom: 8px;"><a href="/composicao_receitas_despesas" style="text-decoration: none; color: #555;">Composição Receitas/Despesas</a></li>
                <li style="margin-bottom: 8px;"><a href="/liquidez" style="text-decoration: none; color: #555;">Índices de Liquidez</a></li>
                <li style="margin-bottom: 8px;"><a href="/resultados_gerais" style="text-decoration: none; color: #555;">Resultados Gerais</a></li>
                <li style="margin-bottom: 8px;"><a href="/custo_pessoal" style="text-decoration: none; color: #555;">Custo de Pessoal</a></li>
                <li style="margin-bottom: 8px;"><a href="/centro_custos" style="text-decoration: none; color: #555;">Análise por Centro de Custos</a></li>
                <li style="margin-bottom: 8px;"><a href="/comparativo_receitas" style="text-decoration: none; color: #555;">Comparativo de Receitas</a></li>
                <li style="margin-bottom: 8px;"><a href="/comparativo_despesas" style="text-decoration: none; color: #555;">Comparativo de Despesas</a></li>
"""

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    # 1. Localiza o texto "Análises Contábeis" (que é o título do menu)
    idx_titulo = c.find('Análises Contábeis')
    if idx_titulo == -1:
        print(f"[AVISO] {arq} nao tem 'Análises Contábeis'.")
        continue

    # 2. Encontra a tag <ul> imediatamente após o título (o submenu)
    idx_ul = c.find('<ul', idx_titulo)
    if idx_ul == -1:
        print(f"[AVISO] {arq} nao encontrei a <ul> do submenu.")
        continue

    # 3. Encontra o fechamento </ul> desse submenu
    idx_fim_ul = c.find('</ul>', idx_ul)
    if idx_fim_ul == -1:
        print(f"[AVISO] {arq} nao encontrei o </ul>.")
        continue

    # 4. Substitui TUDO entre a abertura e o fechamento da <ul> pela lista limpa
    c_novo = c[:idx_ul] + '<ul>' + links_oficiais + '            </ul>' + c[idx_fim_ul+5:]

    shutil.copy2(arq, f"{arq}.bak_limpeza_final_{ts}")
    open(arq, "w", encoding="utf-8").write(c_novo)
    alterados += 1
    print(f"[OK] {arq} - Submenu limpo e DFC inserido.")

print(f"\n[OK] {alterados} arquivos alterados.")
