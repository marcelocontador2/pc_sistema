p = 'notas_explicativas.html'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# Adiciona uma versão nova no script do MCASP (força o navegador a baixar)
import re
if '?v=mcasp_20261111' not in s:
    # Procura o script que contém 'gerarAutoMCASP' e adiciona a versão
    s = re.sub(r'(<script[^>]*?)\s*>', r'\1?v=mcasp_20261111>', s, count=1)

# Salva o arquivo
with open(p, 'w', encoding='utf-8') as f:
    f.write(s)
print("OK: Cache-buster injetado no HTML!")
