import re, os

print("=" * 70)
print("AUDITORIA: COMPARATIVO DE DESPESAS - REGRA DE PDF")
print("=" * 70)

# ==========================================
# 1. FRONTEND: analise_comparativo_despesas.html
# ==========================================
print("\n--- 1. FRONTEND (analise_comparativo_despesas.html) ---")
front_path = r"pc_frontend\analise_comparativo_despesas.html"
if os.path.exists(front_path):
    c = open(front_path, encoding='utf-8-sig').read()
    
    # Botão de PDF
    match = re.search(r'(<button[^>]*>.*?Gerar PDF.*?</button>)', c, re.IGNORECASE | re.DOTALL)
    if match:
        print(f"Botão: {match.group(1).strip()[:200]}")
    
    # Função JS
    match_func = re.search(r'(function gerarPDF[^\{]*\{.*?\n\s{8}\})', c, re.DOTALL)
    if match_func:
        print(f"Função:\n{match_func.group(1)[:500]}")
    else:
        print("[FALTA] Função gerarPDF não encontrada.")
    
    # Envia historico_id?
    if 'historico_id=' in c:
        print("\n[OK] Envia historico_id para o backend")
    else:
        print("\n[FALTA] Não envia historico_id (usa window.print ou periodo atual)")

# ==========================================
# 2. BACKEND: main.py - Rota de Despesas
# ==========================================
print("\n" + "=" * 70)
print("2. BACKEND (main.py - rota gerar_pdf_comparativo_despesas)")
print("=" * 70)

c_back = open(r"pc_backend\main.py", encoding='utf-8-sig').read()
match_rota = re.search(r'(@app\.get\("/gerar_pdf_comparativo_despesas".*?)(?=\n@app\.|\Z)', c_back, re.DOTALL)

if match_rota:
    codigo = match_rota.group(1)
    # Assinatura
    sig = re.search(r'def gerar_pdf_comparativo_despesas\(([^\)]*)\)', codigo)
    if sig:
        print(f"Assinatura: def gerar_pdf_comparativo_despesas({sig.group(1)})")
        if 'historico_id' in sig.group(1):
            print("  [OK] Aceita historico_id")
        else:
            print("  [FALTA] Não aceita historico_id")
    
    # URL do Playwright
    url_match = re.search(r'url\s*=\s*f?"([^"]+)"', codigo)
    if url_match:
        print(f"URL Playwright: {url_match.group(1)}")
else:
    print("[ERRO] Rota não encontrada.")

# ==========================================
# 3. RELATÓRIO: relatorio_comparativo_despesas.html
# ==========================================
print("\n" + "=" * 70)
print("3. RELATÓRIO (relatorio_comparativo_despesas.html)")
print("=" * 70)

rel_path = r"pc_frontend\relatorio_comparativo_despesas.html"
if os.path.exists(rel_path):
    c_rel = open(rel_path, encoding='utf-8').read()
    if 'historico_comparativo_despesas' in c_rel:
        print("[OK] O relatório busca dados do histórico")
    else:
        print("[FALTA] O relatório não busca dados do histórico (vai buscar do CSV atual)")
else:
    print(f"[ERRO] Arquivo {rel_path} não encontrado.")

# ==========================================
# 4. RESUMO
# ==========================================
print("\n" + "=" * 70)
print("RESUMO")
print("=" * 70)
print("Se as três etapas acima estiverem com [OK], a Despesa já está na regra.")
print("Se faltar alguma, precisamos aplicar o mesmo ajuste que fizemos em Receitas.")
