p = 'pc_frontend/notas_explicativas.html'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# Insere as tags de no-cache logo após o <head>
no_cache_tags = """
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
"""
if 'Cache-Control' not in s:
    s = s.replace('<head>', '<head>' + no_cache_tags, 1)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)
    print("OK: Metatags de no-cache adicionadas ao HTML.")
else:
    print("AVISO: Metatags de no-cache já estavam no HTML.")
