import re

path = "panorama.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Substitui a funcao preencherCards pelo mapeamento correto das chaves do JSON
padrao = re.compile(r'function\s+preencherCards\([^)]*\)\s*\{.*?\n\}', re.DOTALL)

nova_funcao = '''function preencherCards(data) {
    const cards = document.querySelectorAll('.card');
    if (cards.length === 0) return;

    // Mapeamento exato das chaves do JSON para a ordem dos cards na tela
    const valores = [
        data.caixa_bp || 0,             // Card 1: CAIXA E EQUIVALENTE
        data.ativo_total || 0,          // Card 2: ATIVO TOTAL
        data.passivo_total || 0,        // Card 3: PASSIVO TOTAL
        data.patrimonio_liquido || 0,   // Card 4: PATRIMÔNIO LÍQUIDO
        data.receita_realizada || 0,    // Card 5: RECEITAS REALIZADAS
        data.despesa_empenhada || 0,    // Card 6: DESPESAS EMPENHADAS
        data.superavit_orcamentario || 0, // Card 7: SUPERÁVIT/DÉFICIT ORÇAMENTÁRIO
        data.superavit_patrimonial || 0,  // Card 8: SUPERÁVIT PATRIMONIAL
        data.superavit_financeiro || 0    // Card 9: SUPERÁVIT FINANCEIRO
    ];

    cards.forEach((card, index) => {
        const valor = valores[index] || 0;
        const formatado = "R$ " + (valor / 1000000).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " mi";
        
        const elValor = card.querySelector('h2, .valor, span');
        if (elValor) {
            elValor.innerText = formatado;
        }
    });
}'''

nova_s, n = padrao.subn(nova_funcao, s)

if n > 0:
    with open(path, "w", encoding="utf-8") as f:
        f.write(nova_s)
    print("OK: Mapeamento das chaves do JSON corrigido na funcao preencherCards!")
else:
    print("AVISO: Nao foi possivel encontrar a funcao preencherCards.")
