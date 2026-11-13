import os
import re

# Vamos procurar o HTML e o JS do frontend
candidatos_html = [
    "pc_frontend/analise_comparativo_receitas.html",
    "pc_frontend/comparativo_receitas.html",
    "pc_frontend/templates/analise_comparativo_receitas.html",
]

arquivo_html = None
for c in candidatos_html:
    if os.path.exists(c):
        arquivo_html = c
        break

if not arquivo_html:
    print("❌ HTML da tela de Comparativo de Receitas não encontrado.")
    print("Procurando em pc_frontend...")
    for f in os.listdir("pc_frontend"):
        if "comparativo" in f.lower() and "receita" in f.lower():
            print(f"   - {f}")
    exit()

print(f"✅ HTML encontrado: {arquivo_html}")
print()

with open(arquivo_html, "r", encoding="utf-8") as f:
    html = f.read()

print("=" * 80)
print("🔍 Buscando chamadas de API no HTML/JS:")
print("=" * 80)

# Procura por fetch, axios, $.get, $.ajax
chamadas = re.findall(r'(fetch\([^)]+\)|axios\.\w+\([^)]+\)|\$\.(?:get|post|ajax)\([^)]+\))', html)
if chamadas:
    for c in chamadas:
        print(f"   📡 {c[:200]}")
else:
    print("   Nenhuma chamada fetch/axios/$ encontrada no arquivo.")

print()
print("=" * 80)
print("🔍 Buscando URLs de API mencionadas:")
print("=" * 80)
urls = re.findall(r'[\'"`](/api/[^\'"`]+)[\'"`]', html)
if urls:
    for u in set(urls):
        print(f"   🌐 {u}")
else:
    print("   Nenhuma URL /api/ encontrada.")

print()
print("=" * 80)
print("🔍 Buscando referência a comparativo_receitas_v2:")
print("=" * 80)
if "comparativo_receitas_v2" in html:
    idx = html.find("comparativo_receitas_v2")
    print(f"   ✅ Encontrado! Contexto:")
    print("   " + html[max(0, idx-300):idx+500].replace("\n", "\n   "))
else:
    print("   ❌ 'comparativo_receitas_v2' NÃO aparece no frontend.")
    print("   Isso significa que a tela está chamando uma API DIFERENTE (talvez a antiga).")

print()
print("=" * 80)
print("🔍 Verificando função 'Verificar' / botão:")
print("=" * 80)
# Procura por onclick ou função que trata o botão Verificar
matches = re.findall(r'(function\s+\w*verificar\w*|onclick\s*=\s*[\'"][^\'"]*verificar[^\'"]*[\'"])', html, re.IGNORECASE)
if matches:
    for m in set(matches):
        print(f"   🎯 {m}")
else:
    print("   Nenhuma função 'verificar' encontrada no HTML. Pode estar em um .js separado.")

print()
print("=" * 80)
print("📄 Primeiras 80 linhas do HTML (para referência):")
print("=" * 80)
for i, linha in enumerate(html.split("\n")[:80]):
    print(f"   {i+1:3d}: {linha[:140]}")
