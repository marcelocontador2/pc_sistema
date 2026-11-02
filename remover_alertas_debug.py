c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Remove os alertas de debug
c = c.replace('alert("Iniciando upload...");\n        ', '')
c = c.replace('alert("Resposta do servidor: " + JSON.stringify(result));\n            ', '')
c = c.replace('alert("Upload concluído! Chegou no frontend.")', '')

open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
print("[OK] Alertas de debug removidos!")
