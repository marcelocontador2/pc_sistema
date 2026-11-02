c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Adiciona um alerta dentro do try, logo após o upload ser concluído
trecho = 'const response = await fetch(\'/upload\', {'
if 'alert("Upload concluído! Chegou no frontend.")' not in c:
    c = c.replace(
        'const response = await fetch(\'/upload\', {',
        'alert("Iniciando upload...");\n        const response = await fetch(\'/upload\', {'
    )
    # Adiciona um alerta após a resposta
    c = c.replace(
        'result = await response.json();',
        'result = await response.json();\n            alert("Resposta do servidor: " + JSON.stringify(result));'
    )
    open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
    print("[OK] Alertas de debug adicionados!")
else:
    print("[AVISO] Alertas já existem.")
