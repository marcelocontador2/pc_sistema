import re, shutil, datetime

arquivo = r"pc_frontend\relatorio_consolidado.html"
shutil.copy2(arquivo, f"{arquivo}.bak_numerar_ambos_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Numerar a lista de "Encontrados" na verificação
old_verify = """for (const chave in data.encontrados) {
                        const m = data.encontrados[chave];
                        html += `<div class="modulo-item"><span>${m.nome}</span><span class="modulo-ok">✓ ${m.data_geracao}</span></div>`;
                    }"""

new_verify = """let contador = 0;
                    for (const chave in data.encontrados) {
                        contador++;
                        const m = data.encontrados[chave];
                        html += `<div class="modulo-item"><span>${contador}. ${m.nome}</span><span class="modulo-ok">✓ ${m.data_geracao}</span></div>`;
                    }"""

if old_verify in html:
    html = html.replace(old_verify, new_verify)
    print("[OK] Numeração adicionada na lista de Verificação (Encontrados).")
else:
    print("[AVISO] Bloco de Verificação não encontrado.")

# 2. Numerar a lista de "Faltando" na verificação (usando outro contador)
old_faltando = """data.faltando.forEach(m => {
                        html += `<div class="modulo-item"><span>${m.nome}</span><span class="modulo-faltando">✗ Faltando</span></div>`;
                    });"""

new_faltando = """let contFaltando = 0;
                    data.faltando.forEach(m => {
                        contFaltando++;
                        html += `<div class="modulo-item"><span>${contFaltando}. ${m.nome}</span><span class="modulo-faltando">✗ Faltando</span></div>`;
                    });"""

if old_faltando in html:
    html = html.replace(old_faltando, new_faltando)
    print("[OK] Numeração adicionada na lista de Verificação (Faltando).")
else:
    print("[AVISO] Bloco de Faltando não encontrado.")

# 3. Garantir que a numeração do Exibir está correta (já foi feita, mas vamos confirmar)
if "encontrados++;\n                                html +=" in html:
    print("[INFO] Numeração do Exibir já está aplicada.")

with open(arquivo, "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== PROXIMO PASSO ===")
print("1. NÃO precisa reiniciar o servidor.")
print("2. Aperte Ctrl+Shift+R no navegador.")
print("3. Clique em Verificar Dados e depois em Exibir para ver a numeração.")
