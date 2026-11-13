import re

c = open('relatorio_final.html', encoding='utf-8-sig').read()

# Remove a regra .btn-salvar que está fora do @media print (se existir)
c = re.sub(r'\n\s*\.btn-salvar\s*\{[^}]*display:\s*none\s*!important;[^}]*\}', '', c)

# Verifica se a regra .btn-salvar dentro do @media print existe
if '@media print' in c:
    # Garante que a regra .btn-salvar { display: none } esteja DENTRO do @media print
    if '.btn-salvar { display: none' not in c.split('@media print')[1]:
        # Adiciona a regra dentro do @media print, logo após a abertura
        c = c.replace('@media print {', '@media print {\n            .btn-salvar { display: none !important; }')

open('relatorio_final.html', 'w', encoding='utf-8').write(c)
print("[OK] Regra do botão ajustada! Ele deve aparecer na tela e sumir apenas na impressão.")
