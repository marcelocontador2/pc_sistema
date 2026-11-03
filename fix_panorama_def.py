import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"
front_path = r"pc_frontend\panorama.html"

# ==========================================
# 1. CRIAR A ROTA NO BACKEND
# ==========================================
shutil.copy2(back_path, f"{back_path}.bak_pano_rota_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

# Remove se já existir alguma versão antiga/errada
c_back = re.sub(r'@app\.get\("/gerar_pdf_panorama/\{historico_id\}"\).*?(?=\n@app\.|\Z)', '', c_back, flags=re.DOTALL)

nova_rota = '''
@app.get("/gerar_pdf_panorama/{historico_id}")
def gerar_pdf_panorama(historico_id: int):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time
    
    # Abre a tela do panorama passando o ID do histórico
    url = f"http://127.0.0.1:9994/panorama.html?historico_id={historico_id}&_t={int(time.time())}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3000) # Espera extra para gráficos renderizarem
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=panorama_{historico_id}.pdf"}
    )
'''
c_back += nova_rota
open(back_path, 'w', encoding='utf-8').write(c_back)
print("[OK] Rota /gerar_pdf_panorama/{id} criada no Backend!")

# ==========================================
# 2. SUBSTITUIR A FUNÇÃO GERARPDF E INJETAR O ESPIÃO
# ==========================================
shutil.copy2(front_path, f"{front_path}.bak_pano_rota_{ts}")
c_front = open(front_path, encoding='utf-8').read()

# 2.1 Substitui a função gerarPDF antiga com segurança (contando chaves)
inicio_func = c_front.find('function gerarPDF()')
if inicio_func != -1:
    idx_chave = c_front.find('{', inicio_func)
    nivel = 1
    i = idx_chave + 1
    while nivel > 0 and i < len(c_front):
        if c_front[i] == '{': nivel += 1
        elif c_front[i] == '}': nivel -= 1
        i += 1
    
    nova_func = """function gerarPDF() {
            const check = document.querySelector(".check-historico:checked");
            if (!check) { 
                alert("Atenção: Marque um relatório no histórico antes de gerar o PDF."); 
                return; 
            }
            
            const url = `/gerar_pdf_panorama/${check.value}`;
            const a = document.createElement('a');
            a.href = url;
            a.target = '_blank';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }"""
    c_front = c_front[:inicio_func] + nova_func + c_front[i:]
    print("[OK] Função gerarPDF atualizada para a nova rota!")

# 2.2 Injeta o "espião" para ler o parâmetro da URL (historico_id)
script_espiao = """
    <script>
        document.addEventListener('DOMContentLoaded', async function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');
            
            if (historicoId) {
                console.log("[DEBUG] Lendo Panorama do Histórico ID:", historicoId);
                try {
                    const res = await fetch(`/historico_panorama/${historicoId}`);
                    const data = await res.json();
                    
                    if (data.ok && data.dados) {
                        // Chama a função que já existe na tela para desenhar os dados
                        if (typeof aplicarValores === 'function') {
                            aplicarValores(data.dados);
                            
                            // Atualiza o título do período na tela (opcional, mas deixa o PDF bonito)
                            const titulo = document.getElementById("periodo-titulo");
                            if(titulo && data.periodo) {
                                titulo.innerText = "Histórico: " + data.periodo;
                            }
                        }
                    }
                } catch (e) {
                    console.error("Erro ao carregar dados do histórico:", e);
                }
            }
        });
    </script>
"""

if '</body>' in c_front:
    c_front = c_front.replace('</body>', script_espiao + '\n</body>', 1)
else:
    c_front += script_espiao

open(front_path, 'w', encoding='utf-8').write(c_front)
print("[OK] Espião injetado no panorama.html!")

# ==========================================
# 3. VALIDAR SINTAXE DO PYTHON
# ==========================================
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py 100% validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe no main.py: {e}")
