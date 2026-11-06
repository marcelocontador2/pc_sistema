import re, shutil, datetime, os, ast

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. BACKEND: corrigir assinatura + lógica condicional
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_desp_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Corrige a assinatura
assinatura_antiga = 'def gerar_pdf_comparativo_despesas(periodo_atual: str = "2026-TRIMESTRE-3"):'
assinatura_nova = 'def gerar_pdf_comparativo_despesas(periodo_atual: str = "2026-TRIMESTRE-3", historico_id: int = None):'

if assinatura_antiga in c:
    c = c.replace(assinatura_antiga, assinatura_nova)
    print("[OK] Assinatura corrigida para aceitar historico_id")
else:
    c = re.sub(
        r'def gerar_pdf_comparativo_despesas\(periodo_atual[^\)]*\):',
        'def gerar_pdf_comparativo_despesas(periodo_atual: str = "2026-TRIMESTRE-3", historico_id: int = None):',
        c, count=1
    )
    print("[AVISO] Tentativa via regex aplicada")

# Corrige a URL do Playwright para usar lógica condicional
url_antiga = 'url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas?periodo_atual={periodo_atual}&_t={int(time.time())}"'
url_nova = '''if historico_id:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas?historico_id={historico_id}&_t={int(time.time())}"
    else:
        url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas?periodo_atual={periodo_atual}&_t={int(time.time())}"'''

if url_antiga in c:
    c = c.replace(url_antiga, url_nova)
    print("[OK] URL do Playwright atualizada (lógica condicional)")
else:
    # fallback
    c = re.sub(
        r'url = f"http://127\.0\.0\.1:9994/relatorio_comparativo_despesas\?periodo_atual=\{periodo_atual\}&_t=\{int\(time\.time\(\)\)\}"',
        url_nova,
        c
    )
    print("[AVISO] URL ajustada via regex")

open(back_path, 'w', encoding='utf-8').write(c)

# Valida sintaxe
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")


# ==========================================
# 2. RELATÓRIO: injetar espião para buscar do histórico
# ==========================================
rel_path = r"pc_frontend\relatorio_comparativo_despesas.html"

if os.path.exists(rel_path):
    shutil.copy2(rel_path, f"{rel_path}.bak_desp_{ts}")
    c_rel = open(rel_path, encoding='utf-8').read()
    
    # Remove espião antigo se existir
    c_rel = re.sub(r'<script id="interceptar_historico_despesas">.*?</script>', '', c_rel, flags=re.DOTALL)
    
    # Injeta espião que intercepta fetch da API de despesas
    espiao = """
<script id="interceptar_historico_despesas">
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const historicoId = urlParams.get('historico_id');
    if (!historicoId) return;
    
    // Intercepta o fetch para buscar do histórico de despesas
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        if (url.includes('/api/comparativo_despesas_v2/') || url.includes('/api/comparativo_despesas/')) {
            return originalFetch(`/historico_comparativo_despesas/${historicoId}`, options)
                .then(res => res.json())
                .then(data => {
                    const dados = data.dados ? data.dados : data;
                    return new Response(JSON.stringify(dados), {
                        headers: { 'Content-Type': 'application/json' }
                    });
                });
        }
        return originalFetch(url, options);
    };
});
</script>
"""
    
    if '</body>' in c_rel:
        c_rel = c_rel.replace('</body>', espiao + '\n</body>', 1)
    else:
        c_rel += espiao
    
    open(rel_path, 'w', encoding='utf-8').write(c_rel)
    print("[OK] Espião injetado no relatório de despesas")
else:
    print(f"[ERRO] {rel_path} não encontrado")


# ==========================================
# 3. RESUMO
# ==========================================
print()
print("=" * 70)
print("RESUMO")
print("=" * 70)
print("1. Backend: aceita historico_id + URL condicional")
print("2. Relatório: busca dados do histórico de despesas")
print()
print("=== PRÓXIMOS PASSOS ===")
print("1. REINICIE o servidor (matar processo da porta 9994 + subir de novo)")
print("2. Va na tela Comparativo de Despesas e aperte Ctrl+F5")
print("3. Marque um historico e clique em Gerar PDF")
