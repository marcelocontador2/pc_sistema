import re

with open("configuracoes.html", "r", encoding="utf-8") as f:
    html = f.read()

match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
if not match:
    print("Nenhum <script> encontrado")
    exit(1)

js = match.group(1)

with open("temp_check.js", "w", encoding="utf-8") as f:
    f.write(js)

abre = js.count('{')
fecha = js.count('}')
print("Chaves abertas:", abre)
print("Chaves fechadas:", fecha)

if abre == fecha:
    print("OK: chaves balanceadas")
else:
    faltam = abre - fecha
    print("ERRO: faltam", faltam, "chaves de fechamento")
    linhas = js.split('\n')
    print("\nUltimas 10 linhas do script:")
    for l in linhas[-10:]:
        print("  >", l)

print("\n--- VERIFICACAO DE PARENTESES ---")
print("Parenteses: abre", js.count('('), "| fecha", js.count(')'))
print("Colchetes: abre", js.count('['), "| fecha", js.count(']'))
