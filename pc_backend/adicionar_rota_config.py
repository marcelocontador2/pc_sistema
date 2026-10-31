from pathlib import Path
import ast

arquivo = Path("main.py")
conteudo = arquivo.read_text(encoding="utf-8")

if '@app.get("/configuracoes"' in conteudo:
    print("AVISO: Rota /configuracoes ja existe")
else:
    trecho_antigo = 'app = FastAPI(title="PC - Prestacao de Contas API")'
    rota_nova = '''

@app.get("/configuracoes", response_class=HTMLResponse)
async def serve_configuracoes():
    import os
    html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pc_frontend", "configuracoes.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()
'''
    if trecho_antigo in conteudo:
        conteudo = conteudo.replace(trecho_antigo, trecho_antigo + rota_nova, 1)
        arquivo.write_text(conteudo, encoding="utf-8")
        print("OK: Rota /configuracoes adicionada!")
    else:
        print("ERRO: nao achei o app = FastAPI(...)")

try:
    ast.parse(conteudo)
    print("Sintaxe OK!")
except SyntaxError as e:
    print(f"ERRO de sintaxe: {e}")
