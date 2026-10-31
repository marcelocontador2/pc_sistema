import re

c = open('main.py', encoding='utf-8-sig').read()

# Remove a função antiga (linha 345) que serve o custo_pessoal.html
padrao = r'@app\.get\("/analise_custo_pessoal", response_class=HTMLResponse\)\s*\ndef serve_analise_custo_pessoal\(\):\s*\n\s*html_path = os\.path\.join\(os\.path\.dirname\(os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\), "pc_frontend", "custo_pessoal\.html"\).*?return HTMLResponse\(content=conteudo, headers=headers\)\s*\n'

c = re.sub(padrao, '', c, flags=re.DOTALL)

open('main.py', 'w', encoding='utf-8').write(c)
print('[OK] Função duplicada removida!')
