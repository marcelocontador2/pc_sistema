import re

caminho = "pc_frontend/integridade.html"
with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

print("=" * 70)
print("AUDITORIA DO HTML DA TELA DE INTEGRIDADE")
print("=" * 70)

# 1. Procura todos os IDs no HTML
ids = re.findall(r'id="([^"]+)"', html)
print(f"\n📋 IDs encontrados no HTML ({len(ids)}):")
for i in sorted(set(ids)):
    print(f"   - {i}")

# 2. Procura todos os onclick nos botões
onclicks = re.findall(r'onclick="([^"]+)"', html)
print(f"\n📋 Onclicks nos botões ({len(onclicks)}):")
for o in onclicks:
    print(f"   - {o}")

# 3. Procura todos os selects e seus IDs
selects = re.findall(r'<select[^>]*id="([^"]+)"[^>]*>', html)
print(f"\n📋 IDs dos <select> ({len(selects)}):")
for s in selects:
    print(f"   - {s}")

# 4. Verifica se a função verificarMatriz está no HTML
if 'function verificarMatriz' in html or 'async function verificarMatriz' in html:
    print("\n✅ Função verificarMatriz existe.")
    # Mostra a função
    idx = html.find('function verificarMatriz')
    if idx == -1:
        idx = html.find('async function verificarMatriz')
    if idx != -1:
        i = html.find("{", idx)
        contador = 1
        i += 1
        while i < len(html) and contador > 0:
            if html[i] == "{": contador += 1
            elif html[i] == "}": contador -= 1
            i += 1
        print("\n--- Função verificarMatriz ---")
        print(html[idx:i][:1000])  # primeiros 1000 chars
else:
    print("\n❌ Função verificarMatriz NÃO existe.")

# 5. Verifica se o container da matriz existe
for container_id in ['matriz-container', 'tabela-container', 'resultado', 'matriz']:
    if f'id="{container_id}"' in html:
        print(f"\n✅ Container '{container_id}' existe.")
    else:
        print(f"\n❌ Container '{container_id}' NÃO existe.")
