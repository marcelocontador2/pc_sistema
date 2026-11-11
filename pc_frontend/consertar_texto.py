p = 'notas_explicativas.html'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# O texto que está na sua tela
texto_ruim = "NOTA 1 Â€\" CONTEXTO OPERACIONAL E BASE DE PREPARAÇÍFJO"
texto_bom = "NOTA 1 — CONTEXTO OPERACIONAL E BASE DE PREPARAÇÃO"

# Troca na força
s = s.replace(texto_ruim, texto_bom)

# Salva
with open(p, 'w', encoding='utf-8') as f:
    f.write(s)
print("OK: Texto corrigido na força no arquivo HTML!")
