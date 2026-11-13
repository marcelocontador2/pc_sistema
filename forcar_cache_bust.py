import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_forcar_cache_bust")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza a rota que serve o HTML do relatório consolidado
# e adiciona um parâmetro de versão para forçar o navegador a baixar a versão nova
if "def serve_relatorio_consolidado():" in conteudo:
    idx = conteudo.find("def serve_relatorio_consolidado():")
    i = conteudo.find("{", idx)
    c = 1
    i += 1
    while i < len(conteudo) and c > 0:
        if conteudo[i] == "{": c += 1
        elif conteudo[i] == "}": c -= 1
        i += 1
    
    nova_funcao = '''def serve_relatorio_consolidado():
    from fastapi.responses import FileResponse
    import os
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_consolidado.html")
    # Adiciona um timestamp para forçar o navegador a baixar a versão nova
    headers = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    return FileResponse(caminho, headers=headers)'''
    
    conteudo = conteudo[:idx] + nova_funcao + conteudo[i:]
    print("✅ Rota do HTML ajustada para forçar o navegador a baixar a versão nova.")

# Verifica sintaxe
try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ main.py salvo com sucesso!")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe: {e.lineno}: {e.text}")
