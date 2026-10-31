from pathlib import Path
import ast

arquivo = Path("main.py")
conteudo = arquivo.read_text(encoding="utf-8")

# ============ CORRIGIR PDF COMPLETO ============
# 1. Encontrar a rota do PDF completo
inicio = conteudo.find('@app.get("/gerar_pdf_completo_custo_pessoal")')
if inicio == -1:
    print("ERRO: nao achei a rota do PDF completo")
    exit(1)

# Encontrar o fim da rota (proximo @app.get)
fim = conteudo.find("\n@app.get", inicio + 10)
if fim == -1:
    fim = conteudo.find("\n@app.post", inicio + 10)
if fim == -1:
    fim = len(conteudo)

# Substituir toda a rota por uma versao limpa
nova_rota = '''@app.get("/gerar_pdf_completo_custo_pessoal")
def gerar_pdf_completo_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3"):
    try:
        from playwright.sync_api import sync_playwright
        import os, tempfile

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            url = f"http://127.0.0.1:9999/custo_pessoal_pdf_completo?periodo={periodo}"
            page.goto(url)
            page.wait_for_timeout(4000)  # Espera o fetch do HTML
            pdf_bytes = page.pdf(format="A4", print_background=True)
            browser.close()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=custo_pessoal_completo_{periodo}.pdf"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

'''

conteudo = conteudo[:inicio] + nova_rota + conteudo[fim:]
print("OK: Rota do PDF completo reescrita!")

# ============ CORRIGIR PDF RESUMO ============
inicio2 = conteudo.find('@app.get("/gerar_pdf_custo_pessoal")')
if inicio2 == -1:
    print("ERRO: nao achei a rota do PDF resumo")
    exit(1)

fim2 = conteudo.find("\n@app.get", inicio2 + 10)
if fim2 == -1:
    fim2 = conteudo.find("\n@app.post", inicio2 + 10)
if fim2 == -1:
    fim2 = len(conteudo)

nova_rota2 = '''@app.get("/gerar_pdf_custo_pessoal")
def gerar_pdf_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3"):
    try:
        from playwright.sync_api import sync_playwright
        import os

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            url = f"http://127.0.0.1:9999/custo_pessoal_pdf_resumo?periodo={periodo}"
            page.goto(url)
            page.wait_for_timeout(4000)  # Espera o fetch do HTML
            pdf_bytes = page.pdf(format="A4", print_background=True)
            browser.close()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=custo_pessoal_resumo_{periodo}.pdf"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

'''

conteudo = conteudo[:inicio2] + nova_rota2 + conteudo[fim2:]
print("OK: Rota do PDF resumo reescrita!")

arquivo.write_text(conteudo, encoding="utf-8")

try:
    ast.parse(conteudo)
    print("Sintaxe OK!")
except SyntaxError as e:
    print(f"ERRO de sintaxe: {e}")
