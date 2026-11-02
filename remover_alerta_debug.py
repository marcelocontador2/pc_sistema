c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Remove o alerta de debug da resposta do servidor
c = c.replace('alert("Resposta do servidor: " + JSON.stringify(result));\n', '')

# Se sobrou algum alerta de debug de upload, remove também
c = c.replace('alert("Iniciando upload...");\n', '')

open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
print("[OK] Alerta de debug removido!")
