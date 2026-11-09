arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

# 1. Remove a linha que adiciona a variavel OBSERVACOES
html = re.sub(r'\nconst OBSERVACOES = \{observacoes_json\};', '', html)

# 2. Restaura a funcao tit() para o formato original
funcao_quebrada = re.search(r'function tit\(n, t\) \{.*?\n\}', html, re.DOTALL)
if funcao_quebrada:
    funcao_original = """function tit(n, t) { return '<h2 class="secao-titulo">' + n + '. ' + t + '</h2>'; }"""
    html = html.replace(funcao_quebrada.group(0), funcao_original)
    print("[OK] Funcao tit() restaurada para o original.")
else:
    print("[AVISO] Nao encontrei a funcao tit() modificada.")

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Template restaurado.")
