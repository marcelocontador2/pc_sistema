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

codigo_superavit = """// Calcular Superávit Financeiro (Ativo Financeiro - Passivo Financeiro)
    // 1. Tenta pegar o valor exato direto do JSON (Panorama ou BP)
    let sfAt = null;
    let sfAn = null;
    
    if (D.panorama && D.panorama.superavit_financeiro !== undefined) {
        sfAt = Number(D.panorama.superavit_financeiro);
        sfAn = Number(D.panorama.superavit_financeiro_anterior || 0);
    } else {
        // 2. Se não tiver no JSON, calcula pela fórmula: (Caixa + Créditos) - Passivo Circulante
        const itemCaixa = encontrados.find(e => e.chave.toLowerCase().includes('caixa'));
        const itemCreditos = encontrados.find(e => e.chave.toLowerCase().includes('credito') || e.chave.toLowerCase().includes('crédito'));
        const itemPassivoCirc = encontrados.find(e => e.chave.toLowerCase().includes('passivo_circulante'));
        
        if (itemPassivoCirc) {
            const caixaAt = itemCaixa ? parseFloat(itemCaixa.atual) : 0;
            const caixaAn = itemCaixa ? parseFloat(itemCaixa.anterior) : 0;
            const credAt = itemCreditos ? parseFloat(itemCreditos.atual) : 0;
            const credAn = itemCreditos ? parseFloat(itemCreditos.anterior) : 0;
            const passAt = parseFloat(itemPassivoCirc.atual);
            const passAn = parseFloat(itemPassivoCirc.anterior);
            
            sfAt = (caixaAt + credAt) - passAt;
            sfAn = (caixaAn + credAn) - passAn;
        }
    }
    
    // 3. Se conseguiu calcular/encontrar, joga na tabela
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

print("[OK] Linha de Superávit Financeiro corrigida com a fórmula contábil correta!")
