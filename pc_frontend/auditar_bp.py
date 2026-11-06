import re

arq = "relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

novo_bloco = """// ===== 2. ANÁLISE BP =====
H += tit(2, 'Análise do Balanço Patrimonial');
H += '<div class="desc">Comparativo das contas do Balanço Patrimonial (período atual x anterior).</div>';

const bpRaw = D.analise_bp || D.balanco_patrimonial || D.bp;

if (bpRaw) {
    // Descobre onde estão os dados de verdade
    let bp = null;
    if (bpRaw.dados && typeof bpRaw.dados === 'object' && !Array.isArray(bpRaw.dados)) {
        bp = bpRaw.dados;
    } else {
        bp = bpRaw;
    }
    
    const labels = {
        ativo_circulante:'Ativo Circulante', caixa:'Caixa e Equivalentes',
        creditos:'Créditos a Curto Prazo', ativo_nao_circulante:'Ativo Não Circulante',
        ativo_realizavel:'Ativo Realizável a Longo Prazo', imobilizado:'Imobilizado',
        total_ativo:'TOTAL DO ATIVO', passivo_circulante:'Passivo Circulante',
        passivo_nao_circulante:'Passivo Não Circulante', passivo_total:'Passivo Total',
        patrimonio_liquido:'Patrimônio Líquido', total_passivo:'TOTAL DO PASSIVO'
    };
    
    const rows = [];
    
    // Estratégia 1: buscar chaves específicas conhecidas
    Object.keys(labels).forEach(k => {
        let item = bp[k];
        if (item === undefined && bp.dados) item = bp.dados[k];
        
        if (item !== undefined) {
            let at = 0, an = 0;
            if (typeof item === 'object' && item !== null) {
                at = item.atual !== undefined ? item.atual : (item.valor_atual !== undefined ? item.valor_atual : 0);
                an = item.anterior !== undefined ? item.anterior : (item.valor_anterior !== undefined ? item.valor_anterior : 0);
            } else if (!isNaN(item)) {
                at = item;
            }
            
            let varStr = '-';
            if (an && an !== 0) {
                const varP = ((at - an) / Math.abs(an)) * 100;
                const sinal = varP > 0 ? '+' : '';
                varStr = sinal + varP.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%';
            }
            
            const fAt = 'R$ ' + parseFloat(at).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            const fAn = 'R$ ' + parseFloat(an).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            
            rows.push([labels[k], fAt, fAn, varStr]);
        }
    });
    
    // Estratégia 2: se a estratégia 1 falhou, varre TUDO que tiver atual/anterior
    if (rows.length === 0) {
        Object.keys(bp).forEach(k => {
            const item = bp[k];
            if (item && typeof item === 'object' && 'atual' in item) {
                const at = item.atual || 0;
                const an = item.anterior || 0;
                
                let varStr = '-';
                if (an && an !== 0) {
                    const varP = ((at - an) / Math.abs(an)) * 100;
                    const sinal = varP > 0 ? '+' : '';
                    varStr = sinal + varP.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%';
                }
                
                const fAt = 'R$ ' + parseFloat(at).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                const fAn = 'R$ ' + parseFloat(an).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                
                rows.push([k.replace(/_/g, ' ').toUpperCase(), fAt, fAn, varStr]);
            }
        });
    }
    
    if (rows.length > 0) {
        H += tab(['Conta','Período Atual (R$)','Período Anterior (R$)', 'Var. (%)'], rows);
    } else {
        // Debug final: mostra a estrutura exata para sabermos o que está acontecendo
        H += '<div style="border: 2px solid red; padding: 10px; background: #fff; font-family: monospace; font-size: 11px; color: black;">';
        H += '<b>DEBUG: Nenhuma conta encontrada. Estrutura de bpRaw:</b><br>';
        H += '<pre>' + JSON.stringify(bpRaw, null, 2).substring(0, 2000) + '</pre>';
        H += '</div>';
    }
} else {
    H += '<p>Módulo não encontrado no JSON.</p>';
}
"""

padrao = re.compile(r"(// ===== 2\. ANÁLISE BP =====.*?)(?=// ===== 3\. ANÁLISE BO =====)", re.DOTALL)
html = padrao.sub(novo_bloco, html)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Seção 2 reescrita com auditoria e múltiplas estratégias de leitura.")
