arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# Substitui a função unwrap por uma versão que desembrulha até 2 níveis
old_unwrap = '''function unwrap(mod) {
    if (!mod) return null;
    if (mod.dados !== undefined) return mod.dados;
    return mod;
}'''

new_unwrap = '''function unwrap(mod) {
    if (!mod) return null;
    let cur = mod;
    // Desembrulha até 3 níveis de "dados" (para casos como analise_bp)
    for (let i = 0; i < 3; i++) {
        if (cur && cur.dados !== undefined && (cur.dados === null || typeof cur.dados === 'object')) {
            cur = cur.dados;
        } else {
            break;
        }
    }
    return cur;
}'''

if old_unwrap in html:
    html = html.replace(old_unwrap, new_unwrap)
    with open(arq, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Função unwrap corrigida (desembrulha até 3 níveis).")
else:
    print("[AVISO] Função unwrap antiga não encontrada. Procurando variação...")
    import re
    padrao = re.compile(r'function unwrap\(mod\)\s*\{.*?\n\}', re.DOTALL)
    if padrao.search(html):
        html = padrao.sub(new_unwrap, html)
        with open(arq, "w", encoding="utf-8") as f:
            f.write(html)
        print("[OK] Função unwrap substituída (via regex).")
    else:
        print("[ERRO] Não foi possível encontrar a função unwrap.")
