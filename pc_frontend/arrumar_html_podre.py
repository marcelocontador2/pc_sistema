p = 'notas_explicativas.html'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# O texto exato que está aparecendo na sua tela
texto_podre = "NOTA 1 Â€\" CONTEXTO OPERACIONAL E BASE DE PREPARAÇÍFJO"
texto_limpo = "NOTA 1 — CONTEXTO OPERACIONAL E BASE DE PREPARAÇÃO"

# Substitui o texto podre pelo texto limpo
if texto_podre in s:
    s = s.replace(texto_podre, texto_limpo)
    print("OK: Texto podre encontrado e substituído no HTML!")
else:
    # Se não achar exato, tenta uma abordagem mais agressiva: apaga tudo que tem "NOTA 1"
    import re
    s = re.sub(r'NOTA 1.*?PREPARA.*?ÇÃO', texto_limpo, s, flags=re.DOTALL)
    print("OK: Texto podre tratado com regex no HTML!")

# Salva o arquivo
with open(p, 'w', encoding='utf-8') as f:
    f.write(s)
