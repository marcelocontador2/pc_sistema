import shutil, datetime, ast, os, re

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. CRIAR ROTA NO BACKEND (main.py)
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_integ_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

# Verifica se a rota já existe
if '@app.get("/gerar_pdf_integridade_matriz/{check_id}")' not in c_back:
    nova_rota = '''
@app.get("/gerar_pdf_integridade_matriz/{check_id}")
def gerar_pdf_integridade_matriz(check_id: str):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time
    
    # Abre a tela de integridade com o ID passado
    url = f"http://127.0.0.1:9994/integridade?check={check_id}&_t={int(time.time())}"
    
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
        headers={"Content-Disposition": f"inline; filename=integridade_{check_id}.pdf"}
    )
'''
    ancora = '@app.get("/gerar_pdf_conferencia/{check_id}")'
    if ancora in c_back:
        c_back = c_back.replace(ancora, nova_rota + "\n\n" + ancora, 1)
    else:
        c_back += nova_rota
        
    open(back_path, 'w', encoding='utf-8').write(c_back)
    print("[OK] Rota /gerar_pdf_integridade_matriz/{check_id} criada no Backend!")
else:
    print("[AVISO] Rota já existia no Backend.")

# ==========================================
# 2. ENSINAR A TELA A LER O ID DA URL
# ==========================================
arquivo = r"pc_frontend\integridade.html"
if os.path.exists(arquivo):
    shutil.copy2(arquivo, f"{arquivo}.bak_integ_{ts}")
    c_front = open(arquivo, encoding='utf-8').read()

    # Verifica se já lê o parâmetro da URL
    if "URLSearchParams" not in c_front:
        script_url = """
        <script id="ler_url_integridade">
            document.addEventListener('DOMContentLoaded', function() {
                const urlParams = new URLSearchParams(window.location.search);
                const checkId = urlParams.get('check');
                
                if (checkId) {
                    console.log("Lendo integridade do ID:", checkId);
                    fetch(`/historico_integridade?_t=${Date.now()}`)
                        .then(res => res.json())
                        .then(data => {
                            const item = data.find(x => x.id == checkId);
                            if (item) {
                                // Tenta chamar a função de renderização da tela
                                if (typeof carregarDados === 'function') {
                                    carregarDados(item);
                                } else if (typeof renderizar === 'function') {
                                    renderizar(item);
                                } else {
                                    console.log("Dados do histórico carregados, mas função de render não encontrada.");
                                }
                            }
                        });
                }
            });
        </script>
        """
        if '<head>' in c_front:
            c_front = c_front.replace('<head>', '<head>\n' + script_url, 1)
            open(arquivo, 'w', encoding='utf-8').write(c_front)
            print("[OK] Tela de Integridade atualizada para ler o ID da URL!")
    else:
        print("[OK] Tela de Integridade já lê parâmetros da URL.")
else:
    print("[ERRO] Arquivo integridade.html não encontrado.")

# ==========================================
# 3. VALIDAR SINTAXE
# ==========================================
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py 100% validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe: {e}")
