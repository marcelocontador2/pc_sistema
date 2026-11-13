import re

path = "panorama.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Substitui a funcao preencherCards por uma versao com os IDs reais
padrao = re.compile(r'function\s+preencherCards\([^)]*\)\s*\{.*?\n\}', re.DOTALL)

nova_funcao = '''function preencherCards(data) {
    const mapa = {
        'val-caixa': data.caixa_bp || 0,
        'val-ativo': data.ativo_total || 0,
        'val-passivo': data.passivo_total || 0,
        'val-pl': data.patrimonio_liquido || 0,
        'val-receitas': data.receita_realizada || 0,
        'val-despesas': data.despesa_empenhada || 0,
        'val-superavit-orc': data.superavit_orcamentario || 0,
        'val-superavit-pat': data.superavit_patrimonial || 0,
        'val-superavit-fin': data.superavit_financeiro || 0
    };

    for (const [id, valor] of Object.entries(mapa)) {
        const el = document.getElementById(id);
        if (el) {
            const formatado = "R$ " + (valor / 1000000).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " mi";
            el.innerText = formatado;
        }
    }
}'''

nova_s, n = padrao.subn(nova_funcao, s)

if n > 0:
    with open(path, "w", encoding="utf-8") as f:
        f.write(nova_s)
    print("OK: Funcao preencherCards atualizada com os IDs reais dos cards!")
else:
    print("AVISO: Nao foi possivel encontrar a funcao preencherCards.")
