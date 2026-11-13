import re

with open("panorama.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. ELEMENTOS COM ID NO PAINEL DE HISTÓRICO ===")
# Procura qualquer tag com ID que contenha 'historico'
ids = re.findall(r'id="([^"]*historico[^"]*)"', s, re.IGNORECASE)
if ids:
    for i in ids:
        print(f"  - {i}")
else:
    print("  Nenhum ID com 'historico' encontrado.")
    
    # Procura a div do painel lateral
    print("\n  Procurando tags <ul> ou <div> no menu lateral:")
    match = re.search(r'<div class="side".*?</div>', s, re.DOTALL)
    if match:
        print(match.group(0)[:500])

print("\n=== 2. O QUE O JS ESTA PROCURANDO? ===")
if "document.getElementById('historico-lista')" in s:
    print("  O JS procura por: 'historico-lista'")
elif "document.querySelector('#historico-lista')" in s:
    print("  O JS procura por: '#historico-lista'")
else:
    print("  O JS nao procura por historico-lista (pode estar usando outro seletor).")
