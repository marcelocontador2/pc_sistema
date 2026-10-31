c = open('main.py', encoding='utf-8-sig').read()

# 1. Criar a rota para a tela de configurações
if 'def serve_configuracoes_custo_pessoal' not in c:
    rota_config = r'''
@app.get("/configuracoes_custo_pessoal", response_class=HTMLResponse)
def serve_configuracoes_custo_pessoal():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "configuracoes_custo_pessoal.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Arquivo de configurações não encontrado</h1>", status_code=404)
'''
    if 'if __name__ == "__main__":' in c:
        c = c.replace('if __name__ == "__main__":', rota_config + '\nif __name__ == "__main__":')
    else:
        c += "\n" + rota_config

open('main.py', 'w', encoding='utf-8').write(c)
print('[OK] Rota de configurações criada no main.py!')
