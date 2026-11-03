import re, shutil, datetime, ast, os

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. CRIAR A ROTA NO BACKEND (main.py)
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_patrim_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

if '@app.get("/gerar_pdf_analise_patrimonial/{historico_id}")' not in c_back:
    # Descobre o nome do arquivo HTML de relatório (tenta v2, senão usa o padrão)
    relatorio_html = "relatorio_analise_patrimonial"
    if not os.path.exists(os.path.join("pc_frontend", f"{relatorio_html}.html")):
        for f in os.listdir("pc_frontend"):
            if "relatorio_patrimonial" in f and f.endswith(".html"):
                relatorio_html = f.replace(".html", "")
                break

    nova_rota = f'''
@app.get("/gerar_pdf_analise_patrimonial/{{historico_id}}")
def gerar_pdf_analise_patrimonial(historico_id: int):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time
    
    # Abre a tela do relatório passando o ID do histórico
    url = f"http://127.0.0.1:9994/{relatorio_html}?historico_id={{historico_id}}&_t={{int(time.time())}}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(2000)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={{"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"}})
        browser.close()
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={{"Content-Disposition": f"inline; filename=patrimonial_{{historico_id}}.pdf"}}
    )
'''
    # Insere a rota antes de outra rota de PDF qualquer, ou no final
    ancora = '@app.get("/gerar_pdf_analise_financeira_bf/{id}")'
    if ancora in c_back:
        c_back = c_back.replace(ancora, nova_rota + "\n\n" + ancora, 1)
    else:
        c_back += nova_rota
    
    open(back_path, 'w', encoding='utf-8').write(c_back)
    print(f"[OK] Rota /gerar_pdf_analise_patrimonial/{{id}} criada no Backend (HTML: {relatorio_html})!")
else:
    print("[AVISO] Rota já existia no Backend.")

# ==========================================
# 2. RECONSTRUIR O BOTÃO NO FRONTEND
# ==========================================
front_path = r"pc_frontend\analise_patrimonial.html"
shutil.copy2(front_path, f"{front_path}.bak_patrim_{ts}")
c_front = open(front_path, encoding='utf-8').read()

# Remove qualquer resto de função antiga quebrada
c_front = re.sub(r'function gerarPDFHistorico\(\) \{.*?\n        \}', '', c_front, flags=re.DOTALL)

# Substitui o botão quebrado por um botão perfeito com ID único
botao_perfeito = '<button id="btn-pdf-unico" style="background:#3182ce; color:white; padding:8px 16px; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">Gerar PDF</button>'
c_front = re.sub(r'<(?:button|a|div)[^>]*>.*?Gerar PDF.*?<\/(?:button|a|div)>', botao_perfeito, c_front, flags=re.IGNORECASE | re.DOTALL)

# Injeta o script final de clique
script_final = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const btnPdf = document.getElementById('btn-pdf-unico');
            
            if (btnPdf) {
                btnPdf.addEventListener('click', function() {
                    // Aceita checkbox ou radio marcado
                    const sel = document.querySelector('input[type="checkbox"]:checked') || 
                                document.querySelector('input[type="radio"]:checked');
                    
                    if (!sel) {
                        alert("Atenção: Selecione um item do Histórico Salvo (marque a caixinha) antes de gerar o PDF.");
                        return;
                    }
                    
                    let id = sel.value;
                    if (!id || id === "on") {
                        id = sel.id.replace('check-', '').replace('hist-', '');
                        if (!id) id = sel.getAttribute('data-id');
                    }
                    
                    // Rota correta com ID no path
                    const url = `/gerar_pdf_analise_patrimonial/${id}`;
                    console.log("[DEBUG] Abrindo PDF Patrimonial com ID:", url);
                    
                    const a = document.createElement('a');
                    a.href = url;
                    a.target = '_blank';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                });
                console.log("[DEBUG] Botão PDF Patrimonial configurado!");
            }
        });
    </script>
"""

if '</body>' in c_front:
    c_front = c_front.replace('</body>', script_final + '\n</body>', 1)
else:
    c_front += script_final

open(front_path, 'w', encoding='utf-8').write(c_front)
print("[OK] Frontend da Análise Patrimonial refeito com o botão azul e função ativa!")

# ==========================================
# 3. VALIDAR SINTAXE
# ==========================================
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py 100% validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe no main.py: {e}")
