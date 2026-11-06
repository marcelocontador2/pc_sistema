import re, shutil, datetime, os, ast

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. CORRIGIR A ASSINATURA NO BACKEND
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_receitas_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Corrige a assinatura
assinatura_antiga = 'def gerar_pdf_comparativo_receitas(periodo_atual: str = "2026-TRIMESTRE-3"):'
assinatura_nova = 'def gerar_pdf_comparativo_receitas(periodo_atual: str = "2026-TRIMESTRE-3", historico_id: int = None):'
if assinatura_antiga in c:
    c = c.replace(assinatura_antiga, assinatura_nova)
    print("[OK] Assinatura da rota corrigida para aceitar historico_id")
else:
    print("[AVISO] Assinatura não encontrada. Tentando variação...")
    c = re.sub(
        r'def gerar_pdf_comparativo_receitas\(periodo_atual[^\)]*\):',
        'def gerar_pdf_comparativo_receitas(periodo_atual: str = "2026-TRIMESTRE-3", historico_id: int = None):',
        c, count=1
    )

# Verifica se a URL do Playwright está consistente
if 'relatorio_comparativo_receitas_v2?historico_id' in c:
    print("[OK] URL do Playwright usa historico_id (lógica condicional já existente)")

# Cria rota serve para o relatório se não existir
if '@app.get("/relatorio_comparativo_receitas_v2")' not in c and '@app.get("/relatorio_comparativo_receitas")' not in c:
    # Adiciona rota para servir o relatório
    rota_serve = '''
@app.get("/relatorio_comparativo_receitas_v2")
def serve_relatorio_receitas_v2():
    from fastapi.responses import FileResponse
    import os
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Tenta v2, senão a versão sem v2
    for nome in ["relatorio_comparativo_receitas_v2.html", "relatorio_comparativo_receitas.html"]:
        caminho = os.path.join(base, "pc_frontend", nome)
        if os.path.exists(caminho):
            return FileResponse(caminho)
    return {"erro": True, "mensagem": "Relatório não encontrado"}
'''
    c += rota_serve
    print("[OK] Rota /relatorio_comparativo_receitas_v2 criada (serve o HTML)")

open(back_path, 'w', encoding='utf-8').write(c)

# Valida sintaxe
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")


# ==========================================
# 2. ADICIONAR "ESPIÃO" NO RELATÓRIO
# ==========================================
# Verifica qual arquivo existe
rel_v2 = r"pc_frontend\relatorio_comparativo_receitas_v2.html"
rel_antigo = r"pc_frontend\relatorio_comparativo_receitas.html"

rel_path = rel_v2 if os.path.exists(rel_v2) else rel_antigo
print(f"\n[INFO] Relatório a ser ajustado: {os.path.basename(rel_path)}")

if os.path.exists(rel_path):
    shutil.copy2(rel_path, f"{rel_path}.bak_receitas_{ts}")
    c_rel = open(rel_path, encoding='utf-8').read()
    
    # Remove espião antigo
    c_rel = re.sub(r'<script id="interceptar_historico_receitas">.*?</script>', '', c_rel, flags=re.DOTALL)
    
    # Adiciona novo espião
    espiao = """
<script id="interceptar_historico_receitas">
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const historicoId = urlParams.get('historico_id');
    if (!historicoId) return;
    
    // Intercepta todos os fetches para a API de comparativo
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        if (url.includes('/api/comparativo_receitas_v2/') || url.includes('/api/comparativo_receitas/')) {
            return originalFetch(`/historico_comparativo_receitas/${historicoId}`, options)
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
    print("[OK] Espião injetado no relatório de receitas")
else:
    print("[ERRO] Nenhum relatório de receitas encontrado")

print()
print("=== RESUMO ===")
print("1. Assinatura da rota corrigida (aceita historico_id)")
print("2. Rota /relatorio_comparativo_receitas_v2 criada (serve HTML)")
print("3. Espião injetado no relatório para carregar do histórico")
print()
print("=== TESTE ===")
print("1. Reinicie o servidor (Ctrl+C e suba novamente)")
print("2. Va na tela de Comparativo de Receitas e aperte Ctrl+F5")
print("3. Marque um historico")
print("4. Clique em 'Gerar PDF'")
print("5. O PDF deve sair com os dados do historico marcado")
