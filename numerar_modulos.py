import re, shutil, datetime

arquivo = r"pc_frontend\relatorio_consolidado.html"
shutil.copy2(arquivo, f"{arquivo}.bak_numeracao_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# Altera a linha que constrói o HTML do módulo para incluir o número sequencial
# Vamos usar a variável 'encontrados' (que já existe) como contador e somar +1 na exibição
old_line = '''if (item.nome && item.data_geracao) {
                                html += `<div class="modulo-item"><span>${item.nome}</span><span class="modulo-ok">✓ ${item.data_geracao}</span></div>`;
                                encontrados++;
                            }'''

new_line = '''if (item.nome && item.data_geracao) {
                                encontrados++;
                                html += `<div class="modulo-item"><span>${encontrados}. ${item.nome}</span><span class="modulo-ok">✓ ${item.data_geracao}</span></div>`;
                            }'''

if old_line in html:
    html = html.replace(old_line, new_line)
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Numeração sequencial adicionada aos módulos no Exibir.")
else:
    print("[AVISO] Não encontrei a linha exata para alterar. Verifique se o script anterior foi aplicado.")

print("\n=== PROXIMO PASSO ===")
print("1. NÃO precisa reiniciar o servidor.")
print("2. Aperte Ctrl+Shift+R no navegador.")
print("3. Selecione o histórico e clique em Exibir novamente.")
