import re, os

print("=" * 70)
print("AUDITORIA: COMPARATIVO DE RECEITAS")
print("=" * 70)

# 1. Verifica o botão de PDF no frontend
front_path = r"pc_frontend\analise_comparativo_receitas.html"
if os.path.exists(front_path):
    c = open(front_path, encoding='utf-8-sig').read()
    
    print("\n--- 1. BOTÃO DE PDF NA TELA ---")
    match = re.search(r'(<button[^>]*>.*?Gerar PDF.*?</button>)', c, re.IGNORECASE | re.DOTALL)
    if match:
        print(match.group(1).strip()[:300])
    else:
        print("Botão 'Gerar PDF' não encontrado.")
    
    print("\n--- 2. FUNÇÃO QUE GERA O PDF ---")
    match_func = re.search(r'function gerarPDF[^\(]*\([^\)]*\)\s*\{(.*?)\n\s{8}\}', c, re.DOTALL)
    if match_func:
        print(match_func.group(0)[:600])
    else:
        print("Função gerarPDF não encontrada.")
    
    print("\n--- 3. EXIGE HISTÓRICO? ---")
    if 'check-historico:checked' in c or '.check-historico' in c:
        print("[OK] Verifica se o histórico está marcado")
    else:
        print("[FALTA] Não verifica seleção de histórico")
    
    print("\n--- 4. ENVIA O historico_id? ---")
    if 'historico_id=' in c:
        print("[OK] Envia o ID do histórico para o backend")
        matches = re.findall(r'historico_id=\$\{[^\}]+\}', c)
        for m in matches[:3]:
            print(f"  {m}")
    else:
        print("[FALTA] Não envia historico_id (usa período atual)")
else:
    print(f"[ERRO] Arquivo {front_path} não encontrado.")

# 5. Como está a rota no backend
print("\n" + "=" * 70)
print("BACKEND: ROTA /gerar_pdf_comparativo_receitas")
print("=" * 70)

c_back = open(r"pc_backend\main.py", encoding='utf-8-sig').read()
match_rota = re.search(r'(@app\.get\("/gerar_pdf_comparativo_receitas".*?)(?=\n@app\.|\Z)', c_back, re.DOTALL)

if match_rota:
    codigo = match_rota.group(1)
    
    # Verifica assinatura
    sig = re.search(r'def gerar_pdf_comparativo_receitas\(([^\)]*)\)', codigo)
    if sig:
        print(f"Assinatura: def gerar_pdf_comparativo_receitas({sig.group(1)})")
        if 'historico_id' in sig.group(1):
            print("  [OK] Aceita historico_id como parâmetro")
        else:
            print("  [FALTA] Não aceita historico_id")
    
    # Verifica URL do Playwright
    url_match = re.search(r'url\s*=\s*f?"([^"]+)"', codigo)
    if url_match:
        print(f"\nURL do Playwright: {url_match.group(1)}")
    
    # Verifica se tem lógica condicional
    if 'if historico_id' in codigo:
        print("  [OK] Tem lógica condicional para historico_id")
    else:
        print("  [FALTA] Não tem lógica condicional (sempre usa período atual)")
else:
    print("[ERRO] Rota não encontrada no main.py.")

# 6. Verifica se existe o relatório HTML
print("\n" + "=" * 70)
print("RELATÓRIOS DE RECEITAS NA PASTA")
print("=" * 70)
for f in os.listdir("pc_frontend"):
    if "receita" in f.lower() and f.endswith(".html"):
        print(f"  - {f}")
