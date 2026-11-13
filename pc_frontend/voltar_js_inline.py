import re
import os

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# 1. Le o conteudo do arquivo JS (se existir)
js_content = ""
if os.path.exists("composicao_scripts.js"):
    with open("composicao_scripts.js", "r", encoding="utf-8") as f:
        js_content = f.read()
else:
    print("AVISO: composicao_scripts.js nao encontrado. Usando script padrao.")

# 2. Remove a tag <script src="..."></script> que está quebrada
s = re.sub(r'<script\s+src="composicao_scripts\.js[^"]*"></script>', '', s, flags=re.IGNORECASE)

# 3. Injeta o JavaScript de volta como INLINE (antes do </body>)
script_inline = f'\n<script>\n{js_content}\n</script>\n'

if "</body>" in s:
    s = s.replace("</body>", script_inline + "</body>")
else:
    s += script_inline

with open(path, "w", encoding="utf-8") as f:
    f.write(s)

print("OK: JavaScript voltou a ser INLINE no HTML!")
