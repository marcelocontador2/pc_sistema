from pathlib import Path
import ast

arquivo = Path("main.py")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Adicionar "bypass_csp=True" ou "ignore_https_errors" no browser.new_page()
# (ou desabilitar cache do Chromium)
trecho_antigo = '''            browser = p.chromium.launch()
            page = browser.new_page()'''

trecho_novo = '''            browser = p.chromium.launch()
            context = browser.new_context(bypass_csp=True, ignore_https_errors=True)
            page = context.new_page()
            page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})'''

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo, 1)
    print("OK: Playwright configurado para ignorar cache!")
else:
    print("AVISO: nao achei o trecho do browser.new_page()")

# 2. Adicionar um "cache-buster" na URL (ex: ?v=timestamp)
trecho_antigo2 = 'url = f"http://127.0.0.1:9999/custo_pessoal_pdf_completo?periodo={periodo}"'
trecho_novo2 = 'url = f"http://127.0.0.1:9999/custo_pessoal_pdf_completo?periodo={periodo}&_t=" + str(int(__import__("time").time()))'

if trecho_antigo2 in conteudo:
    conteudo = conteudo.replace(trecho_antigo2, trecho_novo2, 1)
    print("OK: Cache-buster adicionado no PDF completo!")

trecho_antigo3 = 'url = f"http://127.0.0.1:9999/custo_pessoal_pdf_resumo?periodo={periodo}"'
trecho_novo3 = 'url = f"http://127.0.0.1:9999/custo_pessoal_pdf_resumo?periodo={periodo}&_t=" + str(int(__import__("time").time()))'

if trecho_antigo3 in conteudo:
    conteudo = conteudo.replace(trecho_antigo3, trecho_novo3, 1)
    print("OK: Cache-buster adicionado no PDF resumo!")

# 3. Fechar o browser corretamente
trecho_antigo4 = '''            browser.close()'''
trecho_novo4 = '''            context.close()
            browser.close()'''

if trecho_antigo4 in conteudo:
    conteudo = conteudo.replace(trecho_antigo4, trecho_novo4, 1)
    print("OK: Browser fechado corretamente!")

arquivo.write_text(conteudo, encoding="utf-8")

try:
    ast.parse(conteudo)
    print("Sintaxe OK!")
except SyntaxError as e:
    print(f"ERRO de sintaxe: {e}")
