import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_rota_nome_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Corrige a rota para procurar o arquivo sem _v2 (que é o que existe)
rota_antiga = '''@app.get("/relatorio_comparativo_despesas_v2")
def serve_relatorio_despesas_v2():
    from fastapi.responses import FileResponse
    import os
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho = os.path.join(base, "pc_frontend", "relatorio_comparativo_despesas_v2.html")
    if os.path.exists(caminho):
        return FileResponse(caminho)
    return {"erro": True, "mensagem": "Relatorio nao encontrado"}'''

rota_nova = '''@app.get("/relatorio_comparativo_despesas_v2")
def serve_relatorio_despesas_v2():
    from fastapi.responses import FileResponse
    import os
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Procura o _v2 primeiro, senão o sem _v2
    for nome in ["relatorio_comparativo_despesas_v2.html", "relatorio_comparativo_despesas.html"]:
        caminho = os.path.join(base, "pc_frontend", nome)
        if os.path.exists(caminho):
            return FileResponse(caminho)
    return {"erro": True, "mensagem": "Relatorio nao encontrado"}'''

if rota_antiga in c:
    c = c.replace(rota_antiga, rota_nova)
    print("[OK] Rota corrigida para procurar o arquivo correto")
else:
    print("[AVISO] Rota não encontrada com o texto exato. Tentando via regex...")
    padrao = r'@app\.get\("/relatorio_comparativo_despesas_v2"\).*?return \{"erro": True, "mensagem": "Relatorio nao encontrado"\}'
    if re.search(padrao, c, re.DOTALL):
        c = re.sub(padrao, rota_nova, c, flags=re.DOTALL)
        print("[OK] Rota substituída via regex")

# Também corrige a URL do Playwright na rota de geração de PDF
c = c.replace(
    'url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas_v2?historico_id={historico_id}&_t={int(time.time())}"',
    'url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas_v2?historico_id={historico_id}&_t={int(time.time())}"'
)
c = c.replace(
    'url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas_v2?periodo_atual={periodo_atual}&_t={int(time.time())}"',
    'url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas_v2?periodo_atual={periodo_atual}&_t={int(time.time())}"'
)

open(back_path, 'w', encoding='utf-8').write(c)

try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
