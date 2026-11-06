import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/integridade.html"
shutil.copy2(arq, f"{arq}.bak_incorporacao_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Procura o trecho que monta a coluna de conferencia
# A condicao atual e: row.conf && row.conf.includes('(')
# Vamos adicionar uma excecao para 'INCORPORAÇÃO DE ATIVOS'
antigo = """        <td class="${statusClass}">${
            row.conf && row.conf.includes('(')
                ? `<button class="btn-justificar" data-linha="${row.item}" onclick="abrirModalJust('${row.item}', this)" style="color:red; border:none; background:none; cursor:pointer; font-weight:bold; font-size:12px; padding:0;">${row.conf}</button>`
                : row.conf
        }</td>"""

novo = """        <td class="${statusClass}">${
            (row.conf && row.conf.includes('(')) || row.item.toUpperCase().includes('INCORPORAÇÃO DE ATIVOS')
                ? `<button class="btn-justificar" data-linha="${row.item}" onclick="abrirModalJust('${row.item}', this)" style="color:${(row.conf && row.conf.includes('(')) ? 'red' : '#0056b3'}; border:none; background:none; cursor:pointer; font-weight:bold; font-size:12px; padding:0; ${(row.conf === 'OK') ? 'text-decoration:underline;' : ''}">${(row.conf === 'OK') ? 'Justificar' : row.conf}</button>`
                : row.conf
        }</td>"""

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] Condicao ajustada: 'INCORPORACAO DE ATIVOS' tera botao de justificativa sempre.")
else:
    print("[AVISO] Trecho exato nao encontrado. Tentando variacao...")
    # Procura a linha que contem row.conf.includes
    import re
    padrao = re.compile(r'<td class="\$\{statusClass\}">.*?row\.conf.*?</td>', re.DOTALL)
    match = padrao.search(c)
    if match:
        c = c.replace(match.group(), novo, 1)
        open(arq, "w", encoding="utf-8").write(c)
        print("[OK] Trecho encontrado via regex e substituido.")
    else:
        print("[ERRO] Nao foi possivel encontrar o trecho da coluna CONFERENCIA.")
