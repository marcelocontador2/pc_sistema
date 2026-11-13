import re

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Encontra o bloco <script> e adiciona uma versao (cache busting)
if "composicao_scripts.js" not in s:
    # Se o script estiver inline, vamos extrair para um arquivo externo com versao
    match = re.search(r'<script>(.*?)</script>', s, re.DOTALL)
    if match:
        js_content = match.group(1)
        # Salva o JS em um arquivo externo
        with open("composicao_scripts.js", "w", encoding="utf-8") as f:
            f.write(js_content)
        # Substitui o script inline por uma referencia externa com ?v=99
        s = s.replace(match.group(0), '<script src="composicao_scripts.js?v=99"></script>')
        print("OK: JavaScript extraido para arquivo externo e cache busting aplicado (?v=99).")
    else:
        print("AVISO: Nenhum script inline encontrado para extrair.")
else:
    print("OK: O HTML ja referencia um script externo.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
