import shutil, datetime, ast

back_path = r"pc_backend\main.py"
ts = datetime.datetime.now().strftime('%H%M%S')
shutil.copy2(back_path, f"{back_path}.bak_conf_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Verifica se a rota já existe
if '@app.get("/gerar_pdf_conferencia/{check_id}")' not in c:
    nova_rota = '''
@app.get("/gerar_pdf_conferencia/{check_id}")
def gerar_pdf_conferencia(check_id: str):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time
    
    # Abre a tela de conferência com o ID passado
    url = f"http://127.0.0.1:9994/conferencia_nova?check={check_id}&_t={int(time.time())}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(2000)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=conferencia_{check_id}.pdf"}
    )
'''
    # Insere antes da rota de PDF de despesas (ou no final do arquivo)
    ancora = '@app.get("/gerar_pdf_comparativo_despesas")'
    if ancora in c:
        c = c.replace(ancora, nova_rota + "\n\n" + ancora, 1)
    else:
        c += nova_rota
    
    open(back_path, 'w', encoding='utf-8').write(c)
    print("[OK] Rota /gerar_pdf_conferencia/{check_id} criada com sucesso!")
else:
    print("[AVISO] Rota já existia no sistema.")

# Valida a sintaxe
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py 100% validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe: {e}")
