import re

path = "analise_dmpl.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Forca o navegador a baixar a versao nova com v=99
s = re.sub(r'dmpl_functions\.js\?v=\d+', 'dmpl_functions.js?v=99', s)
s = s.replace('dmpl_functions.js"', 'dmpl_functions.js?v=99"')

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("OK: Versao do script forcada para ?v=99!")
