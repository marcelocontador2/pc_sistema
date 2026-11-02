c = open('../pc_frontend/analise_centro_custos.html', encoding='utf-8-sig').read()

# 1. Adicionar um cache-buster para forçar o navegador a baixar a versão nova
if "?v=2" not in c:
    c = c.replace(
        '<button class="btn btn-importar" onclick="document.getElementById(\'file-csv\').click()"',
        '<button class="btn btn-importar" onclick="document.getElementById(\'file-csv\').click()"'
    )
    # Adiciona o log no console para confirmar que o clique foi detectado
    c = c.replace(
        'async function importarCSV(event) {',
        'async function importarCSV(event) {\n            console.log("[DEBUG] importarCSV disparado!");'
    )
    print("[OK] Log de debug adicionado!")
else:
    print("[AVISO] Cache-buster já existia.")

# 2. Forçar o navegador a não usar cache na página (via meta tag)
if '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">' not in c:
    c = c.replace(
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">'
    )

open('../pc_frontend/analise_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] HTML atualizado com debug e anti-cache!")
