arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# Localiza a seção "2. ANÁLISE BP" e substitui pela versão com coluna Var. (%)
import re

padrao = re.compile(
    r"// ===== 2\. ANÁLISE BP =====.*?H \+= tab\(\['Conta','Período Atual','Período Anterior'\], rows\);",
    re.DOTALL
)

nova_secao = '''// ===== 2. ANÁLISE BP =====
H += tit(2, 'Análise do Balanço Patrimonial');
H += '<div class="desc">Comparativo das contas do Balanço Patrimonial (período atual x anterior).</div>';
const bp = unwrap(D.analise_bp);
if (bp) {
    const labels = {
        ativo_circulante:'Ativo Circulante', caixa:'Caixa e Equivalentes',
        creditos:'Créditos a Curto Prazo', ativo_nao_circulante:'Ativo Não Circulante',
        ativo_realizavel:'Ativo Realizável a Longo Prazo', imobilizado:'Imobilizado',
        total_ativo:'TOTAL DO ATIVO', passivo_circulante:'Passivo Circulante',
        passivo_nao_circulante:'Passivo Não Circulante', passivo_total:'Passivo Total',
        patrimonio_liquido:'Patrimônio Líquido', total_passivo:'TOTAL DO PASSIVO'
    };
    function varPct(at, an) {
        if (an === null || an === undefined || an === 0) return '-';
        const v = ((at - an) / Math.abs(an)) * 100;
        return (v >= 0 ? '+' : '') + v.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%';
    }
    const rows = [];
    Object.keys(labels).forEach(k => {
        if (bp[k] && typeof bp[k] === 'object') {
            const at = bp[k].atual;
            const an = bp[k].anterior;
            rows.push([labels[k], moeda(at), moeda(an), varPct(at, an)]);
        }
    });
    H += tab(['Conta','Período Atual','Período Anterior','Var. (%)'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }'''

if padrao.search(html):
    html = padrao.sub(lambda m: nova_secao, html)
    with open(arq, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Seção do BP atualizada (com coluna Var. %).")
else:
    print("[ERRO] Não encontrei o bloco '2. ANÁLISE BP' no template.")
