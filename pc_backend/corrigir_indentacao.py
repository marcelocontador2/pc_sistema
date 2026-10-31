import re

c = open('main.py', encoding='utf-8-sig').read()

# Remove a indentação do @app.get
c = re.sub(r'^\s+@app\.get\("/analise_custo_pessoal", response_class=HTMLResponse\)', '@app.get("/analise_custo_pessoal", response_class=HTMLResponse)', c, flags=re.MULTILINE)

open('main.py', 'w', encoding='utf-8').write(c)
print('[OK] Indentação do @app.get corrigida!')
