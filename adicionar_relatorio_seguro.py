import re, shutil, datetime, os

# =========================================================
# 1. INSERIR O LINK NO MENU (SE AINDA NÃO EXISTIR)
# =========================================================
arquivo = r"pc_frontend\index.html"
backup = f"pc_frontend\\index_backup_consolidado_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

if 'href="/relatorio_consolidado"' not in html:
    # Procura o link de "Configuracoes" (sem acento) para inserir depois
    alvo = '<li><a href="/configuracoes" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Configuracoes</a></li>'
    if alvo in html:
        novo_item = '''
    <li><a href="/relatorio_consolidado" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Relatório Consolidado</a></li>'''
        html = html.replace(alvo, alvo + novo_item, 1)
        print("[OK] Link 'Relatório Consolidado' inserido no menu.")
    else:
        print("[AVISO] Não achei a tag exata de 'Configuracoes'. O link não foi inserido.")
else:
    print("[INFO] Link 'Relatório Consolidado' já existe no menu.")

with open(arquivo, "w", encoding="utf-8") as f:
    f.write(html)

# =========================================================
# 2. GARANTIR QUE A ROTA DO BACKEND EXISTA E APONTE PARA A TELA
# =========================================================
arq_main = r"pc_backend\main.py"
with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

# Se a rota não existir, cria uma
if '@app.get("/relatorio_consolidado"' not in main_code:
    rota = '''
@app.get("/relatorio_consolidado", response_class=HTMLResponse)
def relatorio_consolidado():
    caminho = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_consolidado.html")
    if _os.path.exists(caminho):
        return FileResponse(caminho)
    return HTMLResponse(content="<html><body style='font-family:Arial;padding:50px;text-align:center;'><h1>Relatório Consolidado</h1><p>Em construção.</p><a href='/'>Voltar</a></body></html>")
'''
    main_code += "\n" + rota
    with open(arq_main, "w", encoding="utf-8") as f:
        f.write(main_code)
    print("[OK] Rota /relatorio_consolidado criada no backend.")
else:
    print("[INFO] Rota /relatorio_consolidado já existe.")

# =========================================================
# 3. VERIFICAR SE O HTML DA TELA EXISTE (se não, criar um básico)
# =========================================================
caminho_html = r"pc_frontend\relatorio_consolidado.html"
if not os.path.exists(caminho_html):
    print("[AVISO] O arquivo relatorio_consolidado.html não existe. Criando um básico...")
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório Consolidado</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f4f6f9; }
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        h1 { color: #003366; }
        .btn { padding: 8px 16px; background: #0056b3; color: white; border: none; border-radius: 6px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" style="text-decoration:none; color:#ff7f00; font-weight:bold;">← Voltar</a>
        <h1>Relatório Consolidado</h1>
        <p>Clique no botão abaixo para verificar os dados do período.</p>
        <button class="btn" onclick="alert('Em construção!')">Verificar Dados</button>
    </div>
</body>
</html>""")
    print("[OK] Arquivo relatorio_consolidado.html criado.")
else:
    print("[INFO] O arquivo relatorio_consolidado.html já existe.")

print("\n=== PROXIMO PASSO ===")
print("1. REINICIE O SERVIDOR (Ctrl+C e suba novamente) para o backend carregar a nova rota.")
print("2. No navegador: Ctrl+Shift+R.")
print("3. Clique no menu 'Relatório Consolidado' para abrir a tela base.")
