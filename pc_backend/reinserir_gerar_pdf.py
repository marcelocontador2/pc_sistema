c = open('main.py', encoding='utf-8-sig').read()

# Verifica se as funções já existem (para não duplicar)
if "def gerar_pdf_custo_pessoal" not in c:
    novas_funcoes = r'''
@app.get("/gerar_pdf_custo_pessoal")
def gerar_pdf_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3", entidade: str = None):
    try:
        from playwright.sync_api import sync_playwright
        import sqlite3, os, time
        
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        if id:
            cur.execute("SELECT periodo FROM historico_custo_pessoal WHERE id = ?", (id,))
            row = cur.fetchone()
            if row:
                periodo = row[0]
                print(f"[PDF RESUMO] Historico ID {id} -> periodo {periodo}")
        
        if not entidade:
            cur.execute("SELECT valor FROM configuracoes WHERE chave = 'tipo_entidade'")
            row = cur.fetchone()
            entidade = row[0] if row else "COFEN"
        
        conn.close()
        print(f"[PDF RESUMO] periodo={periodo}, entidade={entidade}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(bypass_csp=True)
            page = context.new_page()
            page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})
            url = f"http://127.0.0.1:9999/custo_pessoal_pdf_resumo?periodo={periodo}&entidade={entidade}&_t=" + str(int(time.time()))
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(2000)
            pdf_bytes = page.pdf(format="A4", print_background=True)
            context.close()
            browser.close()
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=custo_pessoal_resumo_{periodo}.pdf"}
        )
    except Exception as e:
        print(f"[ERRO PDF RESUMO] {e}")
        return Response(content=str(e), media_type="text/plain", status_code=500)

@app.get("/gerar_pdf_completo_custo_pessoal")
def gerar_pdf_completo_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3", entidade: str = None):
    try:
        from playwright.sync_api import sync_playwright
        import sqlite3, os, time
        
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        if id:
            cur.execute("SELECT periodo FROM historico_custo_pessoal WHERE id = ?", (id,))
            row = cur.fetchone()
            if row:
                periodo = row[0]
                print(f"[PDF COMPLETO] Historico ID {id} -> periodo {periodo}")
        
        if not entidade:
            cur.execute("SELECT valor FROM configuracoes WHERE chave = 'tipo_entidade'")
            row = cur.fetchone()
            entidade = row[0] if row else "COFEN"
        
        conn.close()
        print(f"[PDF COMPLETO] periodo={periodo}, entidade={entidade}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(bypass_csp=True)
            page = context.new_page()
            page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})
            url = f"http://127.0.0.1:9999/custo_pessoal_pdf_completo?periodo={periodo}&entidade={entidade}&_t=" + str(int(time.time()))
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(2000)
            pdf_bytes = page.pdf(format="A4", print_background=True)
            context.close()
            browser.close()
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=custo_pessoal_completo_{periodo}.pdf"}
        )
    except Exception as e:
        print(f"[ERRO PDF COMPLETO] {e}")
        return Response(content=str(e), media_type="text/plain", status_code=500)

'''
    # Insere antes do if __name__
    if 'if __name__ == "__main__":' in c:
        c = c.replace('if __name__ == "__main__":', novas_funcoes + '\nif __name__ == "__main__":')
    else:
        c += "\n" + novas_funcoes

open('main.py', 'w', encoding='utf-8').write(c)
print('[OK] Funções de gerar PDF reinseridas!')
