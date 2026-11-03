import re, shutil, datetime, ast, os, glob

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. ENCONTRAR O ARQUIVO E A ROTA DO BACKEND
# ==========================================
front_path = r"pc_frontend\panorama.html"
if not os.path.exists(front_path):
    print("[ERRO] Arquivo panorama.html não encontrado.")
    exit(1)

back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_pano_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

rota_nome = "gerar_pdf_panorama"
if rota_nome not in c_back:
    # Descobre o nome do arquivo de relatório
    relatorio_html = "relatorio_panorama"
    for f in os.listdir("pc_frontend"):
        if "relatorio_panorama" in f and f.endswith(".html"):
            relatorio_html = f.replace(".html", "")
            break

    nova_rota = f'''
@app.get("/{rota_nome}/{{historico_id}}")
def {rota_nome}(historico_id: int):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time
    
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
        headers={{"Content-Disposition": f"inline; filename=panorama_{{historico_id}}.pdf"}}
    )
'''
    c_back += nova_rota
    open(back_path, 'w', encoding='utf-8').write(c_back)
    print(f"[OK] Rota /{rota_nome}/{{id}} criada no Backend! (HTML: {relatorio_html})")
else:
    print("[AVISO] Rota já existia no Backend.")

# ==========================================
# 2. INJETAR SCRIPT SEGURO NO FRONTEND
# ==========================================
shutil.copy2(front_path, f"{front_path}.bak_pano_{ts}")
c_front = open(front_path, encoding='utf-8').read()

# Remove restos de funções antigas quebradas
c_front = re.sub(r'function gerarPDFHistorico\(\) \{.*?\n        \}', '', c_front, flags=re.DOTALL)

script_final = f"""
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const botoes = Array.from(document.querySelectorAll('button, a, div'));
            // Procura o botão que tenha "PDF" no texto
            const btnPdf = botoes.find(b => b.innerText.toUpperCase().includes('PDF'));
            
            if (btnPdf) {{
                // Garante o visual azul padrão
                btnPdf.style.background = '#3182ce';
                btnPdf.style.color = 'white';
                btnPdf.style.padding = '8px 16px';
                btnPdf.style.border = 'none';
                btnPdf.style.borderRadius = '4px';
                btnPdf.style.fontWeight = 'bold';
                btnPdf.style.cursor = 'pointer';
                
                btnPdf.removeAttribute('onclick');
                
                btnPdf.addEventListener('click', function(e) {{
                    e.preventDefault();
                    
                    const sel = document.querySelector('input[type="checkbox"]:checked') || 
                                document.querySelector('input[type="radio"]:checked');
                    
                    if (!sel) {{
                        alert("Atenção: Selecione um item do Histórico Salvo antes de gerar o PDF.");
                        return;
                    }}
                    
                    let id = sel.value;
                    if (!id || id === "on") {{
                        id = sel.id.replace('check-', '').replace('hist-', '');
                        if (!id) id = sel.getAttribute('data-id');
                    }}
                    
                    const url = `/{rota_nome}/${{id}}`;
                    console.log("[DEBUG] Abrindo PDF Panorama:", url);
                    
                    const a = document.createElement('a');
                    a.href = url;
                    a.target = '_blank';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                }});
                console.log("[DEBUG] Botão PDF do Panorama configurado!");
            }} else {{
                console.log("[DEBUG] ERRO: Botão PDF não encontrado na tela.");
            }}
        }});
    </script>
"""

if '</body>' in c_front:
    c_front = c_front.replace('</body>', script_final + '\n</body>', 1)
else:
    c_front += script_final

open(front_path, 'w', encoding='utf-8').write(c_front)
print("[OK] Frontend do Panorama atualizado de forma segura!")

# ==========================================
# 3. VALIDAR SINTAXE
# ==========================================
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py 100% validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe no main.py: {e}")
