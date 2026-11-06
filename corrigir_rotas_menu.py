import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# Mapeamento de rotas erradas -> corretas
correcoes = {
    'href="/custo_pessoal"': 'href="/analise_custo_pessoal"',
    'href="/centro_custos"': 'href="/analise_centro_custos"',
    'href="/comparativo_receitas"': 'href="/analise_comparativo_receitas"',
    'href="/comparativo_despesas"': 'href="/analise_comparativo_despesas"',
}

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c
    alterados = 0

    for antigo, novo in correcoes.items():
        if antigo in c:
            c = c.replace(antigo, novo)
            alterados += 1
            print(f"[OK] {arq} - {antigo} -> {novo}")

    # Tambem corrige a lista linksParaMover (se tiver os nomes antigos)
    # (a lista usa os textos, nao os hrefs, entao nao precisa mudar)

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_corrige_rotas_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - {alterados} correcao(oes) aplicada(s).")
    else:
        print(f"[AVISO] {arq} - Nenhuma correcao necessaria.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
