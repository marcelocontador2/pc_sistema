import re, shutil, datetime, ast, os

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. VERIFICAR/CRIAR ROTA NO BACKEND
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_comp_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

# Verifica se a rota já existe
if '@app.get("/gerar_pdf_composicao_receitas_despesas/{historico_id}")' not in c_back:
    # Descobre o nome do arquivo do relatório HTML
    relatorio_html = "relatorio_composicao_receitas_despesas"
    for f in os.listdir("pc_frontend"):
        if "relatorio_composicao" in f and f.endswith(".html"):
            relatorio_html = f.replace(".html", "")
            break

    nova_rota = f'''
@app.get("/gerar_pdf_composicao_receitas_despesas/{{historico_id}}")
def gerar_pdf_composicao_receitas_despesas(historico_id: int):
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
        headers={{"Content-Disposition": f"inline; filename=composicao_{{historico_id}}.pdf"}}
    )
'''
    c_back += nova_rota
    open(back_path, 'w', encoding='utf-8').write(c_back)
    print(f"[OK] Rota /gerar_pdf_composicao_receitas_despesas/{{id}} criada no Backend! (HTML: {relatorio_html})")
else:
    print("[AVISO] Rota já existia no Backend.")

# ==========================================
# 2. INJETAR SCRIPT SEGURO NO FRONTEND
# ==========================================
front_path = r"pc_frontend\composicao_receitas_despesas.html"
shutil.copy2(front_path, f"{front_path}.bak_comp_{ts}")
c_front = open(front_path, encoding='utf-8').read()

# Remove qualquer resquício de função antiga quebrada
c_front = re.sub(r'function gerarPDFHistorico\(\) \{.*?\n        \}', '', c_front, flags=re.DOTALL)

# Script inteligente que não quebra o layout
script_final = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Procura o botão de Gerar PDF
            const botoes = Array.from(document.querySelectorAll('button, a, div'));
            const btnPdf = botoes.find(b => b.innerText.trim().toUpperCase() === 'GERAR PDF');
            
            if (btnPdf) {
                // Garante o visual azul
                btnPdf.style.background = '#3182ce';
                btnPdf.style.color = 'white';
                btnPdf.style.padding = '8px 16px';
                btnPdf.style.border = 'none';
                btnPdf.style.borderRadius = '4px';
                btnPdf.style.fontWeight = 'bold';
                btnPdf.style.cursor = 'pointer';
                
                // Remove clique antigo quebrado
                btnPdf.removeAttribute('onclick');
                
                // Adiciona a nova regra
                btnPdf.addEventListener('click', function(e) {
                    e.preventDefault();
                    
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
                    
                    const url = `/gerar_pdf_composicao_receitas_despesas/${id}`;
                    console.log("[DEBUG] Abrindo PDF Composição:", url);
                    
                    const a = document.createElement('a');
                    a.href = url;
                    a.target = '_blank';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                });
            }
        });
    </script>
"""

if '</body>' in c_front:
    c_front = c_front.replace('</body>', script_final + '\n</body>', 1)
else:
    c_front += script_final

open(front_path, 'w', encoding='utf-8').write(c_front)
print("[OK] Frontend da Composição atualizado de forma segura (sem quebrar layout)!")

# ==========================================
# 3. VALIDAR SINTAXE DO BACKEND
# ==========================================
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py 100% validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe no main.py: {e}")
