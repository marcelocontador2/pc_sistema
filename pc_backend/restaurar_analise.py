import re

c = open('main.py', encoding='utf-8-sig').read()

# Padrão para encontrar o bloco solto (html_path, with open, conteudo, headers, return)
padrao = r'# Caminho absoluto correto\s*\n\s*html_path = os\.path\.join\(os\.path\.dirname\(os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\), "pc_frontend", "custo_pessoal\.html"\)\s*\n\s*with open\(html_path, "r", encoding="utf-8"\) as f:\s*\n\s*conteudo = f\.read\(\)\s*\n\s*headers = \{.*?\}\s*\n\s*return HTMLResponse\(content=conteudo, headers=headers\)'

# Função correta (serve o custo_pessoal.html)
funcao_limpa = r'''@app.get("/analise_custo_pessoal", response_class=HTMLResponse)
def serve_analise_custo_pessoal():
    html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pc_frontend", "custo_pessoal.html")
    if not os.path.exists(html_path):
        return HTMLResponse(content="<h1>Arquivo custo_pessoal.html não encontrado</h1>", status_code=404)
    with open(html_path, "r", encoding="utf-8") as f:
        conteudo = f.read()
    headers = {"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0", "Pragma": "no-cache", "Expires": "0"}
    return HTMLResponse(content=conteudo, headers=headers)
'''

# Substituir
c = re.sub(padrao, funcao_limpa, c, flags=re.DOTALL)

open('main.py', 'w', encoding='utf-8').write(c)
print('[OK] Bloco solto substituído pela função serve_analise_custo_pessoal!')
