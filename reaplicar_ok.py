arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

# 1. Corrige DVP
padrao_dvp = re.compile(r"(//\s*6\.\s*ANÁLISE\s+DVP.*?)(?=\n\s*//\s*7\.)", re.DOTALL | re.IGNORECASE)
m_dvp = padrao_dvp.search(html)
if m_dvp:
    novo_dvp = """// 6. ANÁLISE DVP
H += tit(6, 'Análise das Variações Patrimoniais');
H += '<div class="desc">Demonstração das Variações Patrimoniais.</div>';
const dvp = unwrap(D.analise_patrimonial);
if (dvp) {
    const labels = { variacoes_ativas:'Variações Ativas (VPA)', transf_recebidas:'Transferências Recebidas', reversao_provisoes:'Reversão de Provisões', variacoes_diminutivas:'Variações Diminutivas (VPD)', pessoal_encargos:'Pessoal e Encargos', servicos_terceiros:'Serviços de Terceiros', transf_concedidas:'Transferências Concedidas', superavit_patrimonial:'Superávit Patrimonial', margem_patrimonial:'Margem Patrimonial (%)' };
    const rows = [];
    Object.keys(labels).forEach(k => {
        if (dvp[k] && typeof dvp[k] === 'object') {
            let fAt, fAn, varStr = '-';
            if (k === 'margem_patrimonial') { fAt = pct(dvp[k].atual); fAn = pct(dvp[k].anterior); } 
            else { fAt = moeda(dvp[k].atual); fAn = moeda(dvp[k].anterior); varStr = varPct(dvp[k].atual, dvp[k].anterior); }
            rows.push([labels[k], fAt, fAn, varStr]);
        }
    });
    H += tab(['Item','Atual','Anterior','Var. (%)'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }
"""
    html = html.replace(m_dvp.group(0), novo_dvp)

# 2. Corrige Regionais (Receitas)
padrao_rec = re.compile(r"(//\s*7\.\s*COMPARATIVO\s+DE\s+RECEITAS.*?)(?=\n\s*//\s*8\.)", re.DOTALL | re.IGNORECASE)
m_rec = padrao_rec.search(html)
if m_rec:
    novo_rec = """// 7. COMPARATIVO DE RECEITAS
H += tit(7, 'Comparativo de Receitas');
H += '<div class="desc">Comparativo consolidado de receitas.</div>';
const crec = unwrap(D.comparativo_receitas);
if (crec) {
    const at = crec.atual || {};
    H += sub('Resumo');
    H += tab(['Indicador','Valor'], [['Receita Orçada', moeda(at.orcado_total)], ['Receita Realizada', moeda(at.realizado_total)], ['% Execução', pct(at.percentual_total)]]);
    if (at.grupos && at.grupos.length) {
        H += sub('Composição por Grupo');
        H += tab(['Grupo','Orçado','Realizado','%'], at.grupos.map(g => [g.nome, moeda(g.orcado), moeda(g.realizado), pct(g.percentual)]));
    }
    if (at.cores && at.cores.length) {
        const mapa = new Map();
        at.cores.forEach(c => {
            const key = (c.nome || 'NÃO INFORMADO').toString().trim().toUpperCase();
            if (!mapa.has(key)) mapa.set(key, { regional: key, orcado: 0, realizado: 0 });
            const item = mapa.get(key);
            item.orcado += Number(c.orcado || 0);
            item.realizado += Number(c.realizado || 0);
        });
        const rows = [];
        let totOrc = 0, totReal = 0;
        [...mapa.values()].sort((a, b) => a.regional.localeCompare(b.regional)).forEach(item => {
            const perc = item.orcado ? (item.realizado / item.orcado * 100) : 0;
            rows.push([item.regional.charAt(0) + item.regional.slice(1).toLowerCase(), moeda(item.orcado), moeda(item.realizado), pct(perc)]);
            totOrc += item.orcado; totReal += item.realizado;
        });
        rows.push(['TOTAL', moeda(totOrc), moeda(totReal), pct(totOrc ? (totReal/totOrc*100) : 0)]);
        H += sub('Desdobramento por Regional');
        H += tab(['Regional','Orçado','Realizado','%'], rows);
    }
} else { H += '<p>Módulo não encontrado.</p>'; }
"""
    html = html.replace(m_rec.group(0), novo_rec)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] DVP e Regionais reaplicados.")
