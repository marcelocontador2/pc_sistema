c = open('main.py', encoding='utf-8-sig').read()

# Verifica se a rota já existe
if "def serve_relatorio_centro_custos" not in c:
    nova_rota = """
@app.get("/relatorio_centro_custos", response_class=HTMLResponse)
def serve_relatorio_centro_custos():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_centro_custos.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatório não encontrado</h1>", status_code=404)
"""
    # Insere antes do if __name__
    if 'if __name__ == "__main__":' in c:
        c = c.replace('if __name__ == "__main__":', nova_rota + '\nif __name__ == "__main__":')
    else:
        c += "\n" + nova_rota
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] Rota criada!")
else:
    print("[AVISO] Rota já existe.")

# Verifica se foi realmente adicionada
if "def serve_relatorio_centro_custos" in open('main.py', encoding='utf-8').read():
    print("[OK] Verificação: a função está no arquivo!")
else:
    print("[ERRO] Verificação: a função NÃO está no arquivo!")
