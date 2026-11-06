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

# Remove a linha antiga de superávit financeiro que estava errada
bloco_atual = re.sub(r"// Calcular Superávit Financeiro.*?rows\.push\(\['SUPERÁVIT FINANCEIRO'.*?\]\);", "", bloco_atual, flags=re.DOTALL)

alvo = "H += tab(['Conta','Período Atual (R$)','Período Anterior (R$)', 'Var. (%)'], rows);"

if alvo not in bloco_atual:
    print("[ERRO] Não encontrei a linha exata do tab() no bloco da Seção 2.")
    raise SystemExit

codigo_superavit = """// --- SUPERÁVIT FINANCEIRO CORRETO ---
    let sfAt = null;
    let sfAn = null;
    
    // 1. Tenta pegar do Panorama (onde o backend geralmente calcula)
    if (D.panorama && D.panorama.superavit_financeiro !== undefined) {
        sfAt = Number(D.panorama.superavit_financeiro);
        sfAn = Number(D.panorama.superavit_financeiro_anterior || 0);
    } 
    // 2. Tenta pegar do Balanço Financeiro
    else if (D.analise_financeira_bf && D.analise_financeira_bf.dados && D.analise_financeira_bf.dados.superavit_financeiro !== undefined) {
        const sf = D.analise_financeira_bf.dados.superavit_financeiro;
        sfAt = sf.atual || sf;
        sfAn = sf.anterior || 0;
    }
    // 3. Se não achou, calcula pela fórmula contábil correta: (Caixa + Créditos) - (Passivo Circ. + Passivo Não Circ.)
    else {
        const itemCaixa = encontrados.find(e => e.chave.toLowerCase().includes('caixa'));
        const itemCreditos = encontrados.find(e => e.chave.toLowerCase().includes('credito') || e.chave.toLowerCase().includes('crédito'));
        const itemPassivoCirc = encontrados.find(e => e.chave.toLowerCase().includes('passivo_circulante'));
        const itemPassivoNaoCirc = encontrados.find(e => e.chave.toLowerCase().includes('passivo_nao_circulante'));
        
        if (itemCaixa && itemCreditos && itemPassivoCirc) {
            const caixaAt = parseFloat(itemCaixa.atual) || 0;
            const caixaAn = parseFloat(itemCaixa.anterior) || 0;
            const credAt = parseFloat(itemCreditos.atual) || 0;
            const credAn = parseFloat(itemCreditos.anterior) || 0;
            const passCircAt = parseFloat(itemPassivoCirc.atual) || 0;
            const passCircAn = parseFloat(itemPassivoCirc.anterior) || 0;
            const passNaoCircAt = itemPassivoNaoCirc ? parseFloat(itemPassivoNaoCirc.atual) : 0;
            const passNaoCircAn = itemPassivoNaoCirc ? parseFloat(itemPassivoNaoCirc.anterior) : 0;
            
            sfAt = (caixaAt + credAt) - (passCircAt + passNaoCircAt);
            sfAn = (caixaAn + credAn) - (passCircAn + passNaoCircAn);
        }
    }
    
    // Se conseguiu obter os valores, joga na tabela
    if (sfAt !== null && sfAn !== null) {
        let sfVar = '-';
        if (sfAn && sfAn !== 0) {
            const varP = ((sfAt - sfAn) / Math.abs(sfAn)) * 100;
            sfVar = (varP > 0 ? '+' : '') + varP.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%';
        }
        rows.push(['SUPERÁVIT FINANCEIRO', 'R$ ' + sfAt.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}), 'R$ ' + sfAn.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}), sfVar]);
    }

    """

novo_bloco = bloco_atual.replace(alvo, codigo_superavit + alvo)
html = html.replace(bloco_atual, novo_bloco)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Superávit Financeiro corrigido com a fórmula contábil completa (Caixa + Créditos - Passivo Total).")
