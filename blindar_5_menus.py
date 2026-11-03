import re, shutil, datetime, os

ts = datetime.datetime.now().strftime('%H%M%S')

# Telas que usam rota no backend e precisam do ajuste
telas = [
    {"html": "analise_custo_pessoal.html", "rota": "gerar_pdf_custo_pessoal", "relatorio": "relatorio_custo_pessoal"},
    {"html": "analise_financeira_bf.html", "rota": "gerar_pdf_analise_financeira_bf", "relatorio": "relatorio_analise_financeira_bf"},
    {"html": "analise_orcamentaria.html", "rota": "gerar_pdf_analise_orcamentaria", "relatorio": "relatorio_analise_orcamentaria"},
    {"html": "analise_patrimonial.html", "rota": "gerar_pdf_analise_patrimonial", "relatorio": "relatorio_analise_patrimonial"},
    {"html": "composicao_receitas_despesas.html", "rota": "gerar_pdf_composicao_receitas_despesas", "relatorio": "relatorio_composicao_receitas_despesas"}
]

# ==========================================
# 1. BLINDAR O BACKEND
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_lote_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

for t in telas:
    # Modifica a assinatura da função
    padrao_def = rf'def {t["rota"]}\([^\)]*\):'
    nova_def = f'def {t["rota"]}(periodo_atual: str = "2026-TRIMESTRE-3", historico_id: int = None):'
    c_back = re.sub(padrao_def, nova_def, c_back, count=1)
    
    # Modifica a URL do Playwright
    padrao_url = rf'url = f"http:\/\/127\.0\.0\.1:9994\/{t["relatorio"]}\?.*?"'
    nova_url = f'''if historico_id:
        url = f"http://127.0.0.1:9994/{t["relatorio"]}?historico_id={{historico_id}}&_t={{int(time.time())}}"
    else:
        url = f"http://127.0.0.1:9994/{t["relatorio"]}?periodo_atual={{periodo_atual}}&_t={{int(time.time())}}"'''
    c_back = re.sub(padrao_url, nova_url, c_back, count=1)

open(back_path, 'w', encoding='utf-8').write(c_back)
print("[OK] Backend atualizado para as 5 rotas!")

# ==========================================
# 2. BLINDAR OS FRONTENDS (Telas)
# ==========================================
for t in telas:
    path = os.path.join("pc_frontend", t["html"])
    if not os.path.exists(path): continue
    
    shutil.copy2(path, f"{path}.bak_lote_{ts}")
    c = open(path, encoding='utf-8').read()

    # Substitui o clique do botão de PDF pela função blindada
    # (Funciona para window.open, window.location.href ou chamadas diretas)
    c = re.sub(r'onclick="[^"]*(?:gerar_pdf|gerarPDF|window\.open)[^"]*"', 'onclick="gerarPDFHistorico()"', c, flags=re.IGNORECASE)
    
    # Remove funções antigas se existirem
    c = re.sub(r'function gerarPDFHistorico\(\) \{.*?\n        \}', '', c, flags=re.DOTALL)
    
    # Injeta a nova função usando a técnica da nova aba (sem bloqueio de pop-up)
    nova_funcao = f"""
        function gerarPDFHistorico() {{
            const sel = document.querySelector('input[name="historico"]:checked');
            if (!sel) {{
                alert("Atenção: Selecione um item do Histórico Salvo antes de gerar o PDF.");
                return;
            }}
            const url = `/{t["rota"]}?historico_id=${{sel.value}}`;
            const a = document.createElement('a');
            a.href = url;
            a.target = '_blank';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }}
    """
    if '</script>' in c:
        c = c.replace('</script>', nova_funcao + '\n    </script>', 1)
    else:
        c += f"<script>{nova_funcao}</script>"

    open(path, 'w', encoding='utf-8').write(c)
    print(f"[OK] Frontend {t['html']} atualizado.")

# ==========================================
# 3. BLINDAR OS RELATÓRIOS (Playwright)
# ==========================================
# Vou injetar um interceptador de fetch nos relatórios. Se a URL tiver historico_id,
# ele busca os dados salvos e "engana" o relatório, entregando o JSON congelado.
for t in telas:
    rel_name = t["relatorio"] + ".html"
    path = os.path.join("pc_frontend", rel_name)
    if not os.path.exists(path):
        # Tenta achar o arquivo com nome similar
        for f in os.listdir("pc_frontend"):
            if t["relatorio"] in f and f.endswith(".html"):
                path = os.path.join("pc_frontend", f)
                break
        if not os.path.exists(path): continue

    c = open(path, encoding='utf-8').read()
    
    if "interceptar_historico" in c: continue # Já foi modificado

    script_intercept = """
    <script id="interceptar_historico">
        (function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');
            
            if (historicoId) {
                const originalFetch = window.fetch;
                window.fetch = function(url, options) {
                    if (url.includes('comparativo_') || url.includes('api/')) {
                        // Descobre qual tabela de histórico buscar baseado na URL
                        let type = 'receitas';
                        if (url.includes('despesas')) type = 'despesas';
                        if (url.includes('custo_pessoal')) type = 'custo_pessoal';
                        
                        return originalFetch(`/historico_comparativo_${type}/${historicoId}`, options)
                            .then(res => res.json())
                            .then(data => {
                                const dadosReais = data.dados ? data.dados : data;
                                // Devolve o formato que o relatório espera
                                return new Response(JSON.stringify(dadosReais), { headers: { 'Content-Type': 'application/json' } });
                            });
                    }
                    return originalFetch(url, options);
                };
            }
        })();
    </script>
    """
    
    # Injeta o interceptor no cabeçalho
    if '<head>' in c:
        c = c.replace('<head>', '<head>\n' + script_intercept, 1)
        open(path, 'w', encoding='utf-8').write(c)
        print(f"[OK] Relatório {os.path.basename(path)} blindado.")

# Validação final do Backend
import ast
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("\n[OK] Sintaxe do main.py 100% validada!")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe do main.py quebrada: {e}")
