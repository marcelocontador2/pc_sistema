import re

c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("1) LINKS DE ANÁLISE NO HTML ESTÁTICO")
print("=" * 70)

# Procura todos os links de análise no HTML
for termo, rota in [
    ("Análise Orçamentária", "/analise_orcamentaria"),
    ("Análise Financeira", "/analise_financeira_bf"),
    ("Análise DFC", "/analise_dfc"),
    ("Análise Patrimonial", "/analise_patrimonial"),
    ("Conferência", "/conferencia"),
    ("Integridade", "/integridade"),
    ("Composição", "/composicao_receitas_despesas"),
    ("Liquidez", "/liquidez"),
    ("Resultados", "/resultados_gerais"),
]:
    # Conta ocorrências de href
    count_href = c.count(f'href="{rota}"')
    # Conta ocorrências no JS (textContent)
    count_js = c.count(f"textContent = '{termo}")
    
    print(f"\n{termo}:")
    print(f"  href=\"{rota}\" -> {count_href} ocorrência(s)")
    print(f"  textContent = '{termo}...' -> {count_js} ocorrência(s)")

print("\n" + "=" * 70)
print("2) SCRIPT ORIGINAL QUE CONSTRÓI O SUBMENU")
print("=" * 70)

# Encontra o script que constrói o submenu
idx = c.find("const novoLi = document.createElement('li')")
if idx != -1:
    fim = c.find("</script>", idx) + 9
    print(c[idx:fim])
else:
    print("[AVISO] Nao encontrei o script original de construção do menu.")

print("\n" + "=" * 70)
print("3) SCRIPTS QUE ADICIONAM ITENS AO SUBMENU")
print("=" * 70)

# Encontra todos os blocos que adicionam itens ao submenu
for m in re.finditer(r"textContent\s*=\s*['\"]([^'\"]+)['\"]", c):
    print(f"  textContent = '{m.group(1)}'")

print("\n" + "=" * 70)
print("4) ELEMENTOS NO HTML ESTÁTICO (links de análise)")
print("=" * 70)

for m in re.finditer(r'<a href="(/analise_[^"]+|/conferencia|/integridade|/composicao_receitas_despesas|/liquidez|/resultados_gerais)"[^>]*>([^<]+)</a>', c):
    print(f"  href=\"{m.group(1)}\" -> \"{m.group(2)}\"")
