arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

# Localiza a Seção 2 atual
padrao = re.compile(r"(// ===== 2\. ANÁLISE BP =====.*?)(?=\n// ===== 3\.)", re.DOTALL)
m = padrao.search(html)

if not m:
    print("[ERRO] Não achei a seção 2 no arquivo.")
    raise SystemExit

bloco_antigo = m.group(1)

# Novo bloco de debug: ele vai cuspir na tela o que o backend mandou
novo_bloco = """// ===== 2. ANÁLISE BP =====
H += tit(2, 'Análise do Balanço Patrimonial');
H += '<div class="desc">Comparativo das contas do Balanço Patrimonial (período atual x anterior).</div>';

// --- INÍCIO DO DEBUG ---
H += '<div style="border: 2px solid red; padding: 10px; background: #fff; font-family: monospace; font-size: 12px; color: black;">';
H += '<h3 style="color: red; margin-top: 0;">DEBUG DO BALANÇO PATRIMONIAL</h3>';
try {
    const bpRaw = unwrap(D.analise_bp) || D.balanco_patrimonial || D.bp;
    if (bpRaw) {
        H += '<b>O objeto D.analise_bp existe!</b><br><br>';
        H += '<b>Chaves encontradas:</b> ' + Object.keys(bpRaw).join(', ') + '<br><br>';
        H += '<b>Conteúdo completo (primeiros 1000 caracteres):</b><br>';
        H += '<pre style="white-space: pre-wrap;">' + JSON.stringify(bpRaw, null, 2).substring(0, 1000) + '...</pre>';
    } else {
        H += '<b style="color:red;">ERRO: O objeto D.analise_bp está vazio ou não existe no JSON!</b><br>';
        H += 'Chaves disponíveis em D: ' + Object.keys(D).join(', ');
    }
} catch (e) {
    H += '<b style="color:red;">ERRO DE JAVASCRIPT:</b> ' + e.message;
}
H += '</div>';
// --- FIM DO DEBUG ---
"""

html = html.replace(bloco_antigo, novo_bloco)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Script de varredura injetado na Seção 2!")
