import re

path = "analise_dmpl.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Adiciona ?v=2 no final do link do script (ou atualiza se ja existir)
if 'dmpl_functions.js?v=' in s:
    s = re.sub(r'dmpl_functions\.js\?v=\d+', 'dmpl_functions.js?v=2', s)
else:
    s = s.replace('dmpl_functions.js"', 'dmpl_functions.js?v=2"')

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("OK: Cache do JavaScript atualizado para ?v=2.")
