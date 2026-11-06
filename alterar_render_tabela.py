import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/integridade.html"
shutil.copy2(arq, f"{arq}.bak_render_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Linha 148 atual
antigo = '''        <td class="${statusClass}">${row.conf}</td>'''

# Nova linha: se tiver parêntese (erro), vira botão
novo = '''        <td class="${statusClass}">${
            row.conf && row.conf.includes('(')
                ? `<button class="btn-justificar" data-linha="${row.item}" onclick="abrirModalJust('${row.item}', this)" style="color:red; border:none; background:none; cursor:pointer; font-weight:bold; font-size:12px; padding:0;">${row.conf}</button>`
                : row.conf
        }</td>'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] Funcao renderizarTabela alterada com sucesso.")
    print("[OK] Backup:", f"{arq}.bak_render_{ts}")
else:
    print("[ERRO] Linha exata nao encontrada. Tentando variacao...")
    # Tenta sem espacos iniciais
    antigo2 = '<td class="${statusClass}">${row.conf}</td>'
    if antigo2 in c:
        c = c.replace(antigo2, novo, 1)
        open(arq, "w", encoding="utf-8").write(c)
        print("[OK] Variacao encontrada e alterada.")
    else:
        print("[ERRO] Nao encontrei a linha. Verifique o HTML manualmente.")
