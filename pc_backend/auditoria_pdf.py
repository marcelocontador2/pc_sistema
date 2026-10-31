from pathlib import Path
import ast
import time

print("=== INICIANDO AUDITORIA DO PDF ===")

# 1. Auditoria do HTML
html_path = Path("../pc_frontend/custo_pessoal_pdf_completo.html")
if not html_path.exists():
    print("[ERRO] HTML não encontrado no caminho esperado.")
else:
    html = html_path.read_text(encoding="utf-8")
    
    # Corrige o texto chumbado
    if "(50% da RCL)" in html:
        print("[!] Corrigindo texto chumbado (50% da RCL)...")
        html = html.replace("Limite Resolução Cofen 814/2026 (50% da RCL)", "Limite Resolução Cofen 814/2026 (<span id='pdf-limite-pct-text'>50%</span> da RCL)")
    
    # Corrige o percentual fixo no resumo
    if '<td class="right">50,00%</td>' in html:
        print("[!] Corrigindo percentual fixo no resumo...")
        html = html.replace('<td class="right">50,00%</td>', '<td class="right" id="pdf-resumo-limite-pct">50,00%</td>')
    
    # Garante que o JS atualize o percentual
    if "pdf-resumo-limite-pct" not in html:
         print("[!] Injetando JS para atualizar o percentual do resumo...")
         html = html.replace(
             "document.getElementById('pdf-resumo-limite').innerText = fmt(limite);",
             "document.getElementById('pdf-resumo-limite').innerText = fmt(limite); var pctEl2 = document.getElementById('pdf-resumo-limite-pct'); if (pctEl2) pctEl2.innerText = (limite_pct * 100).toFixed(2) + '%';"
         )

    html_path.write_text(html, encoding="utf-8")
    print("[OK] HTML auditado e corrigido.")

# 2. Auditoria do Backend (main.py)
main_path = Path("main.py")
main_code = main_path.read_text(encoding="utf-8")

# 2.1 Corrigir valor padrão da entidade
if 'entidade: str = "COFEN"' in main_code:
    print("[!] Corrigindo valor padrão da entidade no main.py...")
    main_code = main_code.replace('entidade: str = "COFEN"', 'entidade: str = None')
    print("[OK] Entidade agora inicia como None.")

# 2.2 Forçar o Playwright a ignorar o cache
if 'page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})' not in main_code:
    print("[!] Injetando headers anti-cache no Playwright...")
    main_code = main_code.replace(
        'browser = p.chromium.launch()\n            page = browser.new_page()',
        'browser = p.chromium.launch()\n            context = browser.new_context(bypass_csp=True)\n            page = context.new_page()\n            page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})'
    )

# 2.3 Adicionar cache-buster na URL (timestamp)
if '&_t=' not in main_code:
    print("[!] Adicionando cache-buster (timestamp) nas URLs do PDF...")
    main_code = main_code.replace(
        'url = f"http://127.0.0.1:9999/custo_pessoal_pdf_completo?periodo={periodo}&entidade={entidade}"',
        'url = f"http://127.0.0.1:9999/custo_pessoal_pdf_completo?periodo={periodo}&entidade={entidade}&_t={int(time.time())}"'
    )
    main_code = main_code.replace(
        'url = f"http://127.0.0.1:9999/custo_pessoal_pdf_resumo?periodo={periodo}&entidade={entidade}"',
        'url = f"http://127.0.0.1:9999/custo_pessoal_pdf_resumo?periodo={periodo}&entidade={entidade}&_t={int(time.time())}"'
    )

main_path.write_text(main_code, encoding="utf-8")

try:
    ast.parse(main_code)
    print("[OK] main.py sem erros de sintaxe.")
except Exception as e:
    print(f"[ERRO] Sintaxe do main.py: {e}")

print("=== AUDITORIA FINALIZADA ===")
