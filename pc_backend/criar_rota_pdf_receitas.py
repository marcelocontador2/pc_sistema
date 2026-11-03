c = open('main.py', encoding='utf-8-sig').read()

if 'def gerar_pdf_comparativo_receitas' not in c:
    nova_rota = r'''
@app.get("/gerar_pdf_comparativo_receitas")
def gerar_pdf_comparativo_receitas(periodo_atual: str = "2026-TRIMESTRE-3"):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time, os
    
    url = f"http://127.0.0.1:9994/relatorio_comparativo_receitas_v2?periodo_atual={periodo_atual}&_t={int(time.time())}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3000)  # Espera gráficos renderizarem
        page.evaluate("""() => {
            document.querySelectorAll('canvas').forEach(canvas => {
                const img = document.createElement('img');
                img.src = canvas.toDataURL('image/png');
                img.className = 'canvas-img';
                img.style.cssText = 'display: block; max-width: 100%; max-height: 240px; margin: 0 auto;';
                canvas.parentNode.insertBefore(img, canvas.nextSibling);
            });
        }""")
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=relatorio_receitas_{periodo_atual}.pdf"}
    )
'''
    if 'if __name__ == "__main__":' in c:
        c = c.replace('if __name__ == "__main__":', nova_rota + '\nif __name__ == "__main__":')
    else:
        c += "\n" + nova_rota
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] Rota /gerar_pdf_comparativo_receitas criada!")
else:
    print("[AVISO] Rota já existe.")
