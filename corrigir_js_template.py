import re

arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# Substitui a lógica JS inteira (do "let H = '';" até "document.getElementById('conteudo').innerHTML = H;")
padrao = re.compile(
    r"let H = '';.*?document\.getElementById\('conteudo'\)\.innerHTML = H;",
    re.DOTALL
)

nova_logica = r"""
// Desembrulha o JSON de cada módulo (muitos têm .dados dentro)
function unwrap(mod) {
    if (!mod) return null;
    if (mod.dados !== undefined) return mod.dados;
    return mod;
}

let H = '';

// ===== 1. INTEGRIDADE =====
H += tit(1, 'Integridade entre Demonstrações');
H += '<div class="desc">Matriz de integridade com o cruzamento de todas as demonstrações.</div>';
const integ = unwrap(D.integridade);
if (integ && integ.matriz) {
    const rows = integ.matriz.map(m => [
        m.item || m.NOMENCLATURA || '-',
        m.balancete || m.BALANCETE || '-',
        m.bp || m.BP || '-',
        m.bf || m.BF || '-',
        m.bo || m.BO || '-',
        m.dfc || m.DFC || '-',
        m.dvp || m.DVP || '-',
        m.dmpl || m.DMPL || '-',
        m.conf || m.CONFERENCIA || '-'
    ]);
    H += tab(['Item','Balancete','BP','BF','BO','DFC','DVP','DMPL','Conf.'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }

// ===== 2. ANÁLISE BP =====
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
    const rows = [];
    Object.keys(labels).forEach(k => {
        if (bp[k] && typeof bp[k] === 'object') {
            rows.push([labels[k], moeda(bp[k].atual), moeda(bp[k].anterior)]);
        }
    });
    H += tab(['Conta','Período Atual','Período Anterior'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }

// ===== 3. ANÁLISE BO =====
H += tit(3, 'Análise do Balanço Orçamentário');
H += '<div class="desc">Comparativo das receitas e despesas orçamentárias.</div>';
const bo = unwrap(D.analise_orcamentaria);
if (bo) {
    const campos = [
        ['Receita Realizada','receita_realizada'],
        ['Despesa Empenhada','despesa_empenhada'],
        ['Superávit/Déficit','superavit'],
        ['Restos a Pagar','restos_pagar'],
        ['Receita Orçada','receita_orcada'],
        ['Despesa Orçada','despesa_orcada'],
        ['% Realização Receitas','pct_receita'],
        ['% Realização Despesas','pct_despesa']
    ];
    const rows = [];
    campos.forEach(([label, key]) => {
        const at = bo.atual ? bo.atual[key] : null;
        const an = bo.anterior ? bo.anterior[key] : null;
        rows.push([label, moeda(at), moeda(an)]);
    });
    H += tab(['Indicador','Período Atual','Período Anterior'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }

// ===== 4. ANÁLISE BF =====
H += tit(4, 'Análise do Balanço Financeiro');
H += '<div class="desc">Movimentação financeira consolidada.</div>';
const bf = unwrap(D.analise_financeira_bf);
if (bf) {
    const blocos = [
        ['Receitas', bf.receitas],
        ['Despesas', bf.despesas],
        ['Extraorçamentário', bf.extra],
        ['Caixa', bf.caixa]
    ];
    blocos.forEach(([titulo, obj]) => {
        if (!obj) return;
        H += sub(titulo);
        const rows = [];
        Object.keys(obj).forEach(k => {
            const v = obj[k];
            if (k === 'detalhes') {
                Object.keys(v).forEach(kk => {
                    rows.push(['  ' + kk.replace(/_/g,' ').toUpperCase(), moeda(v[kk].atual), moeda(v[kk].anterior)]);
                });
            } else if (v && typeof v === 'object' && 'atual' in v) {
                rows.push([k.replace(/_/g,' ').toUpperCase(), moeda(v.atual), moeda(v.anterior)]);
            }
        });
        H += tab(['Item','Atual','Anterior'], rows);
    });
} else { H += '<p>Módulo não encontrado.</p>'; }

// ===== 5. ANÁLISE DFC =====
H += tit(5, 'Análise do Fluxo de Caixa');
H += '<div class="desc">Demonstração do Fluxo de Caixa (método direto).</div>';
const dfc = unwrap(D.analise_dfc);
if (dfc) {
    const blocos = [
        ['Fluxo Operacional', dfc.operacional],
        ['Fluxo de Investimento', dfc.investimento],
        ['Fluxo de Financiamento', dfc.financiamento],
        ['Apuração de Caixa', dfc.caixa]
    ];
    blocos.forEach(([titulo, obj]) => {
        if (!obj) return;
        H += sub(titulo);
        const rows = [];
        Object.keys(obj).forEach(k => {
            const v = obj[k];
            if (v && typeof v === 'object' && 'atual' in v) {
                rows.push([k.replace(/_/g,' ').toUpperCase(), moeda(v.atual), moeda(v.anterior)]);
            }
        });
        H += tab(['Item','Atual','Anterior'], rows);
    });
} else { H += '<p>Módulo não encontrado.</p>'; }

// ===== 6. ANÁLISE DVP =====
H += tit(6, 'Análise das Variações Patrimoniais');
H += '<div class="desc">Demonstração das Variações Patrimoniais.</div>';
const dvp = unwrap(D.analise_patrimonial);
if (dvp) {
    const labels = {
        variacoes_ativas:'Variações Ativas (VPA)', transf_recebidas:'Transferências Recebidas',
        reversao_provisoes:'Reversão de Provisões', variacoes_diminutivas:'Variações Diminutivas (VPD)',
        pessoal_encargos:'Pessoal e Encargos', servicos_terceiros:'Serviços de Terceiros',
        transf_concedidas:'Transferências Concedidas', superavit_patrimonial:'Superávit Patrimonial',
        margem_patrimonial:'Margem Patrimonial (%)'
    };
    const rows = [];
    Object.keys(labels).forEach(k => {
        if (dvp[k] && typeof dvp[k] === 'object') {
            const at = dvp[k].atual;
            const an = dvp[k].anterior;
            if (k === 'margem_patrimonial') {
                rows.push([labels[k], pct(at), pct(an)]);
            } else {
                rows.push([labels[k], moeda(at), moeda(an)]);
            }
        }
    });
    H += tab(['Item','Atual','Anterior'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }

// ===== 7. COMPARATIVO DE RECEITAS =====
H += tit(7, 'Comparativo de Receitas');
H += '<div class="desc">Comparativo consolidado de receitas.</div>';
const crec = unwrap(D.comparativo_receitas);
if (crec) {
    const at = crec.atual || {};
    H += sub('Resumo');
    H += tab(['Indicador','Valor'], [
        ['Receita Orçada', moeda(at.orcado_total)],
        ['Receita Realizada', moeda(at.realizado_total)],
        ['% Execução', pct(at.percentual_total)]
    ]);
    if (at.grupos && at.grupos.length) {
        H += sub('Composição por Grupo');
        const rows = at.grupos.map(g => [g.nome, moeda(g.orcado), moeda(g.realizado), pct(g.percentual)]);
        H += tab(['Grupo','Orçado','Realizado','%'], rows);
    }
    if (at.cores && at.cores.length) {
        H += sub('Detalhamento por COREN');
        const rows = at.cores.map(c => [c.nome, moeda(c.orcado), moeda(c.realizado), pct(c.percentual)]);
        H += tab(['COREN','Orçado','Realizado','%'], rows);
    }
} else { H += '<p>Módulo não encontrado.</p>'; }

// ===== 8. COMPARATIVO DE DESPESAS =====
H += tit(8, 'Comparativo de Despesas');
H += '<div class="desc">Comparativo consolidado de despesas.</div>';
const cdesp = unwrap(D.comparativo_despesas);
if (cdesp) {
    const at = cdesp.atual || {};
    H += sub('Resumo');
    H += tab(['Indicador','Valor'], [
        ['Despesa Orçada', moeda(at.orcado_total)],
        ['Despesa Empenhada', moeda(at.empenhado_total)],
        ['Despesa Liquidada', moeda(at.liquidado_total)],
        ['% Execução', pct(at.percentual_total)]
    ]);
    if (at.grupos && at.grupos.length) {
        H += sub('Composição por Grupo');
        const rows = at.grupos.map(g => [g.nome, moeda(g.orcado), moeda(g.empenhado), moeda(g.liquidado), pct(g.percentual)]);
        H += tab(['Grupo','Orçado','Empenhado','Liquidado','%'], rows);
    }
    if (at.detalhes && at.detalhes.length) {
        H += sub('Detalhamento das Despesas');
        const rows = at.detalhes.map(x => [x.nome, moeda(x.orcado), moeda(x.empenhado), pct(x.percentual)]);
        H += tab(['Descrição','Orçado','Empenhado','%'], rows);
    }
} else { H += '<p>Módulo não encontrado.</p>'; }

// ===== 9. LIQUIDEZ =====
H += tit(9, 'Índices de Liquidez e Estrutura');
H += '<div class="desc">Indicadores de liquidez e estrutura patrimonial.</div>';
const liq = unwrap(D.liquidez);
if (liq) {
    H += sub('Liquidez');
    const rowsLiq = [];
    if (liq.liquidez) {
        [['Liquidez Imediata','liquidez_imediata'], ['Liquidez Corrente','liquidez_corrente'],
         ['Liquidez Seca','liquidez_seca'], ['Liquidez Geral','liquidez_geral']].forEach(([label, key]) => {
            if (liq.liquidez[key] !== undefined) rowsLiq.push([label, liq.liquidez[key]]);
        });
    }
    H += tab(['Indicador','Valor'], rowsLiq);

    if (liq.estrutura) {
        H += sub('Estrutura Patrimonial');
        const rowsEst = [];
        [['Endividamento Geral','endividamento_geral'], ['Part. Capital de Terceiros','part_capital_terceiros'],
         ['Imobilização do PL','imobilizacao_pl']].forEach(([label, key]) => {
            if (liq.estrutura[key] !== undefined) rowsEst.push([label, liq.estrutura[key] + '%']);
        });
        H += tab(['Indicador','Valor'], rowsEst);
    }

    if (liq.valores) {
        H += sub('Valores Base');
        const labelsVal = { caixa:'Caixa', ativo_circulante:'Ativo Circulante', estoques:'Estoques',
            realizavel_lp:'Realizável LP', ativo_nao_circulante:'Ativo Não Circulante',
            imobilizado:'Imobilizado', passivo_circulante:'Passivo Circulante',
            passivo_nao_circulante:'Passivo Não Circulante', passivo_total:'Passivo Total',
            ativo_total:'Ativo Total', patrimonio_liquido:'Patrimônio Líquido' };
        const rowsVal = [];
        Object.keys(labelsVal).forEach(k => {
            if (liq.valores[k] !== undefined) rowsVal.push([labelsVal[k], moeda(liq.valores[k])]);
        });
        H += tab(['Item','Valor'], rowsVal);
    }
} else { H += '<p>Módulo não encontrado.</p>'; }

// ===== 10. PANORAMA =====
H += tit(10, 'Panorama de Resultados');
H += '<div class="desc">Resumo executivo dos principais indicadores.</div>';
const pan = unwrap(D.panorama);
if (pan) {
    const labels = {
        ativo_total:'Ativo Total', passivo_total:'Passivo Total', patrimonio_liquido:'Patrimônio Líquido',
        caixa_bp:'Caixa e Equivalentes', receita_realizada:'Receitas Realizadas',
        despesa_empenhada:'Despesas Empenhadas', superavit_orcamentario:'Resultado Orçamentário',
        superavit_patrimonial:'Superávit Patrimonial', superavit_financeiro:'Superávit Financeiro'
    };
    const rows = [];
    Object.keys(labels).forEach(k => {
        if (pan[k] !== undefined) rows.push([labels[k], moeda(pan[k])]);
    });
    H += tab(['Indicador','Valor'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }

// ===== 11. CENTRO DE CUSTOS =====
H += tit(11, 'Análise por Centro de Custos');
H += '<div class="desc">Distribuição das despesas por centro de custo (atual x anterior).</div>';
const cc = unwrap(D.centro_custos);
if (cc && cc.centros) {
    const at = cc.centros || [];
    const an = cc.centros_anterior || [];
    const mapa = {};
    at.forEach(x => { mapa[x.nome] = {at: x.valor, an: 0}; });
    an.forEach(x => { if (mapa[x.nome]) mapa[x.nome].an = x.valor; else mapa[x.nome] = {at: 0, an: x.valor}; });
    const rows = [];
    let totalAt = 0, totalAn = 0;
    Object.keys(mapa).sort().forEach(nome => {
        const {at: va, an: vb} = mapa[nome];
        totalAt += va; totalAn += vb;
        const variacao = vb ? ((va - vb) / Math.abs(vb)) * 100 : 0;
        rows.push([nome, moeda(va), moeda(vb), pct(variacao)]);
    });
    rows.push(['TOTAL', moeda(totalAt), moeda(totalAn), pct(totalAn ? ((totalAt-totalAn)/Math.abs(totalAn))*100 : 0)]);
    H += tab(['Centro de Custo','Atual','Anterior','Variação'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }

// ===== 12. CUSTO DE PESSOAL =====
H += tit(12, 'Custo de Pessoal');
H += '<div class="desc">Custo de pessoal x limite legal (Resolução Cofen 814/2026).</div>';
const cp = unwrap(D.custo_pessoal);
if (cp) {
    H += sub('Composição do Custo');
    H += tab(['Item','Atual','Anterior','Total'], [
        ['Pessoal e Encargos', moeda(cp.pessoal_atual), moeda(cp.pessoal_anterior), moeda(cp.pessoal_total)],
        ['Outras Despesas Variáveis', moeda(cp.outras_atual), moeda(cp.outras_anterior), moeda(cp.outras_total)],
        ['Terceirização', moeda(cp.terc_atual), moeda(cp.terc_anterior), moeda(cp.terc_total)],
        ['CUSTO TOTAL (Bruto)', moeda(cp.custo_atual), moeda(cp.custo_anterior), moeda(cp.custo_total)],
        ['RCL Total (12 meses)', moeda(cp.rcl_atual), moeda(cp.rcl_anterior), moeda(cp.rcl_total)]
    ]);
    H += sub('Limite e Margem');
    H += tab(['Item','Valor'], [
        ['Limite Resolução Cofen 814/2026', moeda(cp.limite_total)],
        ['Margem Disponível', moeda(cp.margem_disponivel_total)],
        ['% Custo sobre RCL', pct(cp.pct_custo_total)],
        ['Faixa de Controle', cp.faixa_controle || '-']
    ]);
} else { H += '<p>Módulo não encontrado.</p>'; }

document.getElementById('conteudo').innerHTML = H;
"""

if padrao.search(html):
    html = padrao.sub(nova_logica, html)
    with open(arq, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Lógica JS do template corrigida (com unwrap).")
else:
    print("[ERRO] Não encontrei o bloco JS para substituir.")
