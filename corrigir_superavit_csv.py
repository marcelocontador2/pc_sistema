import re

arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

padrao = re.compile(r"(// ===== 2\. ANÁLISE BP =====.*?)(?=// ===== 3\. ANÁLISE BO =====)", re.DOTALL)
m = padrao.search(html)

if not m:
    print("[ERRO] Bloco da Seção 2 não encontrado.")
    raise SystemExit

bloco_atual = m.group(1)

# Remove a linha antiga de superávit financeiro (seja qual for o cálculo anterior)
bloco_atual = re.sub(r"// --- SUPERÁVIT FINANCEIRO.*?(?=H \+= tab\(\[\'Conta\')", "", bloco_atual, flags=re.DOTALL)

alvo = "H += tab(['Conta','Período Atual (R$)','Período Anterior (R$)', 'Var. (%)'], rows);"

codigo_superavit = """// --- SUPERÁVIT FINANCEIRO ---
    var sfAt = null;
    var sfAn = null;

    // 1. Busca a chave exata que veio do BP CSV (ex: superavit_financeiro)
    var chaveSf = Object.keys(bp).find(function(k) { 
        return k.toLowerCase().replace(/[áàâãä]/g, 'a').indexOf('superavit') > -1; 
    });

    if (chaveSf) {
        var itemSf = bp[chaveSf];
        if (itemSf && typeof itemSf === 'object' && 'atual' in itemSf) {
            sfAt = Number(itemSf.atual);
            sfAn = Number(itemSf.anterior || 0);
        } else if (typeof itemSf === 'number') {
            sfAt = itemSf;
            sfAn = 0;
        }
    }

    // 2. Se não achou no BP, calcula pela fórmula correta: (Caixa + Créditos) - (Passivo Circulante + Passivo Não Circulante)
    if (sfAt === null) {
        var itemCaixa = encontrados.find(function(e) { return e.chave.toLowerCase().includes('caixa'); });
        var itemCreditos = encontrados.find(function(e) { return e.chave.toLowerCase().includes('credito') || e.chave.toLowerCase().includes('crédito'); });
        var itemPassivoCirc = encontrados.find(function(e) { return e.chave.toLowerCase().includes('passivo_circulante'); });
        var itemPassivoNaoCirc = encontrados.find(function(e) { return e.chave.toLowerCase().includes('passivo_nao_circulante'); });

        if (itemCaixa && itemCreditos && itemPassivoCirc) {
            var caixaAt = parseFloat(itemCaixa.atual) || 0;
            var caixaAn = parseFloat(itemCaixa.anterior) || 0;
            var credAt = parseFloat(itemCreditos.atual) || 0;
            var credAn = parseFloat(itemCreditos.anterior) || 0;
            var passCircAt = parseFloat(itemPassivoCirc.atual) || 0;
            var passCircAn = parseFloat(itemPassivoCirc.anterior) || 0;
            var passNaoCircAt = itemPassivoNaoCirc ? parseFloat(itemPassivoNaoCirc.atual) : 0;
            var passNaoCircAn = itemPassivoNaoCirc ? parseFloat(itemPassivoNaoCirc.anterior) : 0;

            sfAt = (caixaAt + credAt) - (passCircAt + passNaoCircAt);
            sfAn = (caixaAn + credAn) - (passCircAn + passNaoCircAn);
        }
    }

    // 3. Adiciona à tabela
    if (sfAt !== null) {
        var sfVar = '-';
        if (sfAn && sfAn !== 0) {
            var varP = ((sfAt - sfAn) / Math.abs(sfAn)) * 100;
            sfVar = (varP > 0 ? '+' : '') + varP.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%';
        }
        rows.push(['SUPERÁVIT FINANCEIRO', 'R$ ' + sfAt.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}), 'R$ ' + sfAn.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}), sfVar]);
    }

    """

novo_bloco = bloco_atual.replace(alvo, codigo_superavit + alvo)
html = html.replace(bloco_atual, novo_bloco)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Superávit Financeiro corrigido! Agora ele busca direto do CSV ou usa a fórmula contábil correta.")
