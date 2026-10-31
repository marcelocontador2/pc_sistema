import re

c = open('main.py', encoding='utf-8-sig').read()

# Remove o import solto que ficou dentro da função
c = c.replace('    from fastapi.responses import HTMLResponse\n', '')

# Remove o @app.get duplicado que ficou fantasma
c = re.sub(r'@app\.get\("/custo_pessoal_pdf_completo", response_class=HTMLResponse\)\s*\n\s*\n', '', c)

open('main.py', 'w', encoding='utf-8').write(c)
print('[OK] main.py limpo!')
