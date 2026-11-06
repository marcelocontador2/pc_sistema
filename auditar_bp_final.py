import re

arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

novo_bloco = """// ===== 2. ANÁLISE BP =====
H += tit(2, 'Análise do Balanço Patrimonial');
H += '<div class="desc">Comparativo das contas do Balanço Patrimonial (período atual x anterior).</div>';

// Função que desembrulha recursivamente e busca qualquer item com 'atual' e 'anterior'
function coletarBP(obj, prefixo, result) {
    if (!obj || typeof obj !== 'object' || Array.isArray(obj)) return;
    Object.keys(obj).forEach(k => {
        const v = obj[k];
        if (v && typeof v === 'object' && !Array.isArray(v)) {
            if ('atual' in v && 'anterior' in v) {
                result.push({ chave: prefixo + k, atual: v.atual, anterior: v.anterior });
            } else {
                coletarBP(v, prefixo + k + '.', result);
            }
        }
    });
}

const bpRaiz = D.analise_bp || D.balanco_patrimonial || D.bp;
if (bpRaiz) {
    const encontrados = [];
    coletarBP(bpRaiz, '', encontrados);
    
    if (encontrados.length > 0) {
        const rows = encontrados.map(e => {
            const at = parseFloat(e.atual) || 0;
            const an = parseFloat(e.anterior) || 0;
            let varStr = '-';
            if (an && an !== 0) {
                const varP = ((at - an) / Math.abs(an)) * 100;
                varStr = (varP > 0 ? '+' : '') + varP.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%';
            }
            const fAt = 'R$ ' + at.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            const fAn = 'R$ ' + an.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            // Limpa o prefixo da chave para mostrar apenas o nome da conta
            let nome = e.chave.replace(/^dados\\./, '').replace(/^dados\\./, '').replace(/_/g, ' ').toUpperCase();
            return [nome, fAt, fAn, varStr];
        });
        H += tab(['Conta','Período Atual (R$)','Período Anterior (R$)', 'Var. (%)'], rows);
    } else {
        H += '<div style="border: 2px solid red; padding: 10px; background: #fff; font-family: monospace; font-size: 10px;">';
        H += '<b>DEBUG: Nenhuma conta encontrada. Estrutura recebida:</b><br>';
        H += '<pre>' + JSON.stringify(bpRaiz, null, 2).substring(0, 3000) + '</pre>';
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

print("[OK] Seção 2 reescrita com varredura recursiva (desembrulha qualquer nível).")
