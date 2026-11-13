import re

path = "panorama.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Substitui a funcao preencherCards por uma versao que preenche pela ordem dos cards
padrao = re.compile(r'function\s+preencherCards\([^)]*\)\s*\{.*?\n\}', re.DOTALL)

nova_funcao = '''function preencherCards(data) {
    // Pega todos os cards na ordem em que aparecem na tela
    const cards = document.querySelectorAll('.card');
    if (cards.length === 0) return;

    // Mapeamento das chaves do JSON para a ordem dos cards (conforme a tela)
    const valores = [
        data.caixa || 0,
        data.ativo_total || 0,
        data.passivo_total || 0,
        data.patrimonio_liquido || 0,
        data.receitas || 0,
        data.despesas || 0,
        data.superavit || 0,
        data.superavit_patrimonial || 0,
        data.superavit_financeiro || 0
    ];

    // Preenche cada card com o valor correspondente
    cards.forEach((card, index) => {
        const valor = valores[index] || 0;
        const formatado = "R$ " + (valor / 1000000).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " mi";
        
        // Procura o elemento que exibe o valor dentro do card (geralmente h2 ou span)
        const elValor = card.querySelector('h2, .valor, span');
        if (elValor) {
            elValor.innerText = formatado;
        } else {
            // Se nao encontrar, tenta substituir o texto do card inteiro
            // (mas isso pode apagar o titulo, entao cuidado)
            console.warn("Elemento de valor nao encontrado no card", index);
        }
    });
}'''

nova_s, n = padrao.subn(nova_funcao, s)

if n > 0:
    with open(path, "w", encoding="utf-8") as f:
        f.write(nova_s)
    print("OK: Funcao preencherCards atualizada para preencher pela ordem dos cards!")
else:
    print("AVISO: Nao foi possivel encontrar a funcao preencherCards.")
