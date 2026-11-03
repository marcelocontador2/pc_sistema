import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"
front_path = r"pc_frontend\analise_financeira_bf.html"

# ==========================================
# 1. BLINDAR O BACKEND (main.py)
# ==========================================
shutil.copy2(back_path, f"{back_path}.bak_bf_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

# 1.1 Altera a assinatura da função
assinatura_antiga = 'def gerar_pdf_analise_financeira_bf(periodo_atual: str = "2026-TRIMESTRE-3"):'
assinatura_nova = 'def gerar_pdf_analise_financeira_bf(periodo_atual: str = "2026-TRIMESTRE-3", historico_id: int = None):'
c_back = c_back.replace(assinatura_antiga, assinatura_nova)

# 1.2 Altera a URL do Playwright (usando replace exato para não bagunçar a indentação)
url_antiga = '    url = f"http://127.0.0.1:9994/relatorio_analise_financeira_bf?periodo_atual={periodo_atual}&_t={int(time.time())}"'
url_nova = '''    if historico_id:
        url = f"http://127.0.0.1:9994/relatorio_analise_financeira_bf?historico_id={historico_id}&_t={int(time.time())}"
    else:
        url = f"http://127.0.0.1:9994/relatorio_analise_financeira_bf?periodo_atual={periodo_atual}&_t={int(time.time())}"'''

if url_antiga in c_back:
    c_back = c_back.replace(url_antiga, url_nova)
    print("[OK] URL do Playwright no backend atualizada (Análise Financeira).")
else:
    # Fallback caso o nome do arquivo tenha variação
    print("[AVISO] URL exata não encontrada. Tentando substituição via Regex...")
    padrao_url = r'url = f"http://127\.0\.0\.1:9994/([^\"]*analise_financeira[^\"]*)\?periodo_atual=\{periodo_atual\}&_t=\{int\(time\.time\(\)\)\}"'
    match = re.search(padrao_url, c_back)
    if match:
        nome_arquivo = match.group(1)
        url_antiga_regex = match.group(0)
        url_nova_regex = f'''if historico_id:
        url = f"http://127.0.0.1:9994/{nome_arquivo}?historico_id={{historico_id}}&_t={{int(time.time())}}"
    else:
        url = f"http://127.0.0.1:9994/{nome_arquivo}?periodo_atual={{periodo_atual}}&_t={{int(time.time())}}"'''
        c_back = c_back.replace(url_antiga_regex, url_nova_regex)
        print(f"[OK] URL ajustada via Regex (Arquivo: {nome_arquivo}).")

open(back_path, 'w', encoding='utf-8').write(c_back)

# ==========================================
# 2. BLINDAR O FRONTEND (analise_financeira_bf.html)
# ==========================================
shutil.copy2(front_path, f"{front_path}.bak_bf_{ts}")
c_front = open(front_path, encoding='utf-8').read()

# 2.1 Substitui a chamada do botão
c_front = re.sub(r'onclick="[^"]*(?:gerar_pdf_analise_financeira_bf|window\.open)[^"]*"', 'onclick="gerarPDFHistorico()"', c_front, flags=re.IGNORECASE)

# 2.2 Remove funções antigas se existirem
c_front = re.sub(r'function gerarPDFHistorico\(\) \{.*?\n        \}', '', c_front, flags=re.DOTALL)

# 2.3 Injeta a nova função blindada (abre em nova aba)
nova_funcao = """
        function gerarPDFHistorico() {
            const sel = document.querySelector('input[name="historico"]:checked');
            if (!sel) {
                alert("Atenção: Selecione um item do Histórico Salvo antes de gerar o PDF.");
                return;
            }
            const url = `/gerar_pdf_analise_financeira_bf?historico_id=${sel.value}`;
            const a = document.createElement('a');
            a.href = url;
            a.target = '_blank';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
"""

if '</script>' in c_front:
    c_front = c_front.replace('</script>', nova_funcao + '\n    </script>', 1)
else:
    c_front += f"<script>{nova_funcao}</script>"

open(front_path, 'w', encoding='utf-8').write(c_front)
print("[OK] Tela de Análise Financeira atualizada (botão exige histórico).")

# ==========================================
# 3. VALIDAÇÃO DE SINTAXE
# ==========================================
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py 100% validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe no main.py: {e}")
