import re

c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

print("=" * 70)
print("BUSCANDO ROTAS E FUNÇÕES DE CONFERÊNCIA NO MAIN.PY")
print("=" * 70)

# Busca qualquer coisa que tenha "conferencia" no decorator ou nome de função
matches = re.finditer(r'(@app\.(?:get|post)\([^)]+\)\s*\ndef\s+([a-zA-Z0-9_]*conferencia[a-zA-Z0-9_]*\([^)]*\)))', c, re.IGNORECASE)

encontrou = False
for m in matches:
    print("\n" + "-"*40)
    print(m.group(1))
    encontrou = True

if not encontrou:
    print("\n[AVISO] Nenhuma rota de 'conferencia' encontrada no main.py.")

print("\n" + "=" * 70)
print("COMO O HTML CHAMA A ROTA:")
print("=" * 70)
html = open(r"pc_frontend\conferencia_nova.html", encoding="utf-8-sig").read()
# Acha o trecho exato onde o onclick ou window.open está
match_html = re.search(r'.{0,100}gerar_pdf_conferencia.{0,100}', html)
if match_html:
    print(match_html.group(0))
