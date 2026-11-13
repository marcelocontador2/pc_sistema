p = 'notas_explicativas.html'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# Substitui APENAS a URL da rota do botão do MCASP (sem tocar no resto)
s = s.replace("fetch('/api/notas_mcasp/gerar_auto'", "fetch('/api/notas_mcasp/gerar_auto_v2'")
s = s.replace('fetch("/api/notas_mcasp/gerar_auto"', 'fetch("/api/notas_mcasp/gerar_auto_v2"')

with open(p, 'w', encoding='utf-8') as f:
    f.write(s)
print("OK: Botao do MCASP apontando para a rota v2!")
