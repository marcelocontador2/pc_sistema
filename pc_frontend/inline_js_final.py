import re
import os

# 1. Le o conteudo do arquivo JS
js_path = "dmpl_functions.js"
if not os.path.exists(js_path):
    print("ERRO: dmpl_functions.js nao encontrado!")
    exit()

with open(js_path, "r", encoding="utf-8") as f:
    js_content = f.read()

# 2. Remove TODAS as tags <script> que referenciam dmpl_functions.js
path = "analise_dmpl.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Remove qualquer script src que contenha dmpl_functions.js
s = re.sub(r'<script\s+src="[^"]*dmpl_functions\.js[^"]*"></script>', '', s, flags=re.IGNORECASE)

# 3. Remove qualquer script inline antigo que contenha "function carregar()"
# (para evitar duplicacao)
s = re.sub(r'<script>\s*function carregar\(\).*?</script>', '', s, flags=re.DOTALL)

# 4. Injeta o novo script inline antes do </body>
script_inline = f'\n<script>\n{js_content}\n</script>\n'

if "</body>" in s:
    s = s.replace("</body>", script_inline + "</body>")
else:
    s += script_inline

with open(path, "w", encoding="utf-8") as f:
    f.write(s)

print("OK: JavaScript embutido diretamente no HTML!")
