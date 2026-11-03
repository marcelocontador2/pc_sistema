c = open('main.py', encoding='utf-8-sig').read()

if 'def serve_relatorio_comparativo_receitas_v2' not in c:
    nova_rota = r'''
@app.get("/relatorio_comparativo_receitas_v2", response_class=HTMLResponse)
def serve_relatorio_comparativo_receitas_v2():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_comparativo_receitas.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Relatório não encontrado</h1>", status_code=404)
'''
    if 'if __name__ == "__main__":' in c:
        c = c.replace('if __name__ == "__main__":', nova_rota + '\nif __name__ == "__main__":')
    else:
        c += "\n" + nova_rota
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] Rota /relatorio_comparativo_receitas_v2 criada!")
else:
    print("[AVISO] Rota já existe.")
