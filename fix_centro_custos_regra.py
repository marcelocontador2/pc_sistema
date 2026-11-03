import re, shutil, datetime, ast, os

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. CRIAR A ROTA NO BACKEND (main.py)
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_centro_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

if '@app.get("/gerar_pdf_centro_custos/{historico_id}")' not in c_back:
    nova_rota = '''
@app.get("/gerar_pdf_centro_custos/{historico_id}")
def gerar_pdf_centro_custos(historico_id: int):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time
    
    # Abre o relatório v2 passando o ID do histórico
    url = f"http://127.0.0.1:9994/relatorio_centro_custos_v2?historico_id={historico_id}&_t={int(time.time())}"
    
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
        headers={"Content-Disposition": f"inline; filename=centro_custos_{historico_id}.pdf"}
    )
'''
    c_back += nova_rota
    open(back_path, 'w', encoding='utf-8').write(c_back)
    print("[OK] Rota /gerar_pdf_centro_custos/{id} criada no Backend!")
else:
    print("[AVISO] Rota já existia no Backend.")

# ==========================================
# 2. SUBSTITUIR A FUNÇÃO gerarPDF NO FRONTEND
# ==========================================
front_path = r"pc_frontend\analise_centro_custos.html"
shutil.copy2(front_path, f"{front_path}.bak_centro_{ts}")
c_front = open(front_path, encoding='utf-8').read()

inicio = c_front.find('function gerarPDF() {')
if inicio != -1:
    # Conta chaves para achar o fim da função
    idx_chave = c_front.find('{', inicio)
    nivel = 1
    i = idx_chave + 1
    while nivel > 0 and i < len(c_front):
        if c_front[i] == '{': nivel += 1
        elif c_front[i] == '}': nivel -= 1
        i += 1
    
    nova_func = """function gerarPDF() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { 
                alert('Atenção: Selecione um item do Histórico Salvo antes de gerar o PDF.'); 
                return; 
            }
            const url = `/gerar_pdf_centro_custos/${check.value}`;
            window.open(url, '_blank');
        }"""
    
    c_front = c_front[:inicio] + nova_func + c_front[i:]
    open(front_path, 'w', encoding='utf-8').write(c_front)
    print("[OK] Função gerarPDF() atualizada com a regra de negócio no Frontend!")
else:
    print("[AVISO] Função gerarPDF() não encontrada no HTML.")

# ==========================================
# 3. INJETAR O ESPIÃO NO RELATÓRIO V2
# ==========================================
rel_path = r"pc_frontend\relatorio_centro_custos_v2.html"
if os.path.exists(rel_path):
    shutil.copy2(rel_path, f"{rel_path}.bak_centro_{ts}")
    c_rel = open(rel_path, encoding='utf-8').read()
    
    if "interceptar_historico" not in c_rel:
        script_espiao = """
    <script id="interceptar_historico">
        (function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');
            
            if (historicoId) {
                const originalFetch = window.fetch;
                window.fetch = function(url, options) {
                    if (url.includes('/api/') || url.includes('/historico_')) {
                        return originalFetch(`/historico_centro_custos/${historicoId}`, options)
                            .then(res => res.json())
                            .then(data => {
                                const dadosReais = data.dados ? data.dados : data;
                                return new Response(JSON.stringify(dadosReais), { headers: { 'Content-Type': 'application/json' } });
                            });
                    }
                    return originalFetch(url, options);
                };
            }
        })();
    </script>
    """
        if '<head>' in c_rel:
            c_rel = c_rel.replace('<head>', '<head>\n' + script_espiao, 1)
            open(rel_path, 'w', encoding='utf-8').write(c_rel)
            print("[OK] Espião injetado no relatorio_centro_custos_v2.html!")
        else:
            print("[AVISO] Tag <head> não encontrada no relatório.")
else:
    print("[AVISO] Arquivo relatorio_centro_custos_v2.html não encontrado.")

# ==========================================
# 4. VALIDAR SINTAXE
# ==========================================
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py 100% validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe no main.py: {e}")
