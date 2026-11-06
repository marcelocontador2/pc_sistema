import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_rota_desp_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Corrige a URL do Playwright na rota de despesas
url_antiga = 'http://127.0.0.1:9994/relatorio_comparativo_despesas?'
url_nova = 'http://127.0.0.1:9994/relatorio_comparativo_despesas_v2?'

if url_antiga in c:
    c = c.replace(url_antiga, url_nova)
    print("[OK] URL do Playwright corrigida para /relatorio_comparativo_despesas_v2")
else:
    # Tenta variação
    c = c.replace(
        'url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas?historico_id={historico_id}&_t={int(time.time())}"',
        'url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas_v2?historico_id={historico_id}&_t={int(time.time())}"'
    )
    c = c.replace(
        'url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas?periodo_atual={periodo_atual}&_t={int(time.time())}"',
        'url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas_v2?periodo_atual={periodo_atual}&_t={int(time.time())}"'
    )
    print("[OK] URL ajustada manualmente")

# Garante que existe uma rota @app.get("/relatorio_comparativo_despesas_v2")
if '@app.get("/relatorio_comparativo_despesas_v2")' not in c:
    rota = '''
@app.get("/relatorio_comparativo_despesas_v2")
def serve_relatorio_despesas_v2():
    from fastapi.responses import FileResponse
    import os
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho = os.path.join(base, "pc_frontend", "relatorio_comparativo_despesas_v2.html")
    if os.path.exists(caminho):
        return FileResponse(caminho)
    return {"erro": True, "mensagem": "Relatorio nao encontrado"}
'''
    c += rota
    print("[OK] Rota /relatorio_comparativo_despesas_v2 criada")

open(back_path, 'w', encoding='utf-8').write(c)

try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
