html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Relatório Consolidado</title>
<style>
    @page { size: A4 portrait; margin: 15mm; }
    body { font-family: 'Segoe UI', Arial, sans-serif; color: #333; line-height: 1.35; margin: 0; font-size: 10px; }
    
    /* CAPA */
    .capa { text-align: center; padding-top: 60mm; page-break-after: always; }
    .capa .logo { max-height: 80px; margin-bottom: 20px; }
    .capa .faixa { background: #003366; color: white; padding: 35px 0; margin: 15px -15mm 30px -15mm; }
    .capa h1 { color: white; margin: 0; font-size: 30px; letter-spacing: 4px; }
    .capa h2 { color: white; margin: 8px 0 0 0; font-size: 14px; font-weight: normal; }
    .capa .entidade { font-size: 14px; color: #555; margin: 20px 0; }
    .capa .info { background: #f4f6f9; border-left: 5px solid #0056b3; padding: 15px 40px; margin: 15px auto; max-width: 400px; text-align: left; }
    .capa .info .label { font-size: 10px; color: #666; text-transform: uppercase; }
    .capa .info .valor { font-size: 18px; font-weight: bold; color: #003366; margin-top: 5px; }
    .capa .rodape { color: #999; font-size: 10px; margin-top: 50px; }
    
    /* SEÇÕES */
    h2.secao-titulo { color: #003366; border-bottom: 3px solid #003366; padding-bottom: 6px; page-break-before: always; font-size: 18px; margin-bottom: 12px; }
    h3.sub { color: #0056b3; font-size: 11px; margin: 12px 0 6px 0; border-bottom: 1px solid #ddd; padding-bottom: 3px; }
    .desc { font-size: 9px; color: #666; margin-bottom: 8px; font-style: italic; }
    
    /* TABELAS */
    table { width: 100%; border-collapse: collapse; margin: 8px 0; }
    th { background: #003366; color: white; padding: 5px; text-align: left; font-size: 8px; text-transform: uppercase; border: 1px solid #003366; }
    td { padding: 4px 5px; border: 1px solid #ddd; font-size: 8.5px; }
    td.right { text-align: right; }
    td.center { text-align: center; }
    tr:nth-child(even) { background: #f8f9fa; }
    tr.total { font-weight: bold; background: #e9ecef; }
    
    /* CARDS */
    .cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 10px 0; }
    .card { background: #f4f6f9; padding: 10px; border-radius: 5px; border-left: 3px solid #0056b3; }
    .card .label { font-size: 8px; color: #666; text-transform: uppercase; }
    .card .valor { font-size: 14px; font-weight: bold; color: #003366; margin-top: 3px; }
    
    /* STATUS */
    .ok { background: #d4edda; border-left: 4px solid #28a745; padding: 10px; margin: 8px 0; }
    .warn { background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 8px 0; }
    .ok strong, .warn strong { font-size: 12px; }
</style>
</head>
<body>

<div class="capa">
    <img src="logo" class="logo">
    <div class="faixa">
        <h1>RELATÓRIO CONSOLIDADO</h1>
        <h2>Análise Contábil</h2>
    </div>
    <div class="entidade">COFEN - Conselho Federal de Enfermagem</div>
    <div class="info">
        <div class="label">Período de Análise</div>
        <div class="valor">{periodo}</div>
    </div>
    <div class="rodape">Gerado em: {data_geracao}<br>SGPC - Sistema de Gestão de Prestação de Contas</div>
</div>

<div id="conteudo"></div>

<script>
const D = {dados_json};

function moeda(v) {
    if (v === null || v === undefined || isNaN(v)) return 'R$ 0,00';
    v = parseFloat(v);
    return 'R$ ' + v.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
}
function pct(v) {
    if (v === null || v === undefined) return '0,00%';
    return parseFloat(v).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%';
}
function tit(n, t) { return '<h2 class="secao-titulo">' + n + '. ' + t + '</h2>'; }
function sub(t) { return '<h3 class="sub">' + t + '</h3>'; }
function tab(headers, rows) {
    if (!rows.length) return '<p style="color:#999">Sem dados.</p>';
    let h = '<table><thead><tr>';
    headers.forEach((x,i) => h += '<th' + (i>0?' style="text-align:right"':'') + '>' + x + '</th>');
    h += '</tr></thead><tbody>';
    rows.forEach(r => {
        h += '<tr>';
        r.forEach((c,i) => h += '<td' + (i>0?' class="right"':'') + '>' + (c??'-') + '</td>');
        h += '</tr>';
    });
    return h + '</tbody></table>';
}

let H = '';

// ===== 1. INTEGRIDADE (matriz completa) =====
H += tit(1, 'Integridade entre Demonstrações');
H += '<div class="desc">Matriz de integridade com o cruzamento de todas as demonstrações.</div>';
if (D.integridade && D.integridade.matriz) {
    const rows = D.integridade.matriz.map(m => [
        m.item, m.balancete, m.bp, m.bf, m.bo, m.dfc, m.dvp, m.dmpl, m.conf
    ]);
    H += tab(['Item','Balancete','BP','BF','BO','DFC','DVP','DMPL','Conf.'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }

// ===== 2. ANÁLISE BP (todas as contas) =====
H += tit(2, 'Análise do Balanço Patrimonial');
H += '<div class="desc">Comparativo das contas do Balanço Patrimonial (período atual x anterior).</div>';
if (D.analise_bp && D.analise_bp.dados) {
    const d = D.analise_bp.dados;
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
        if (d[k] && typeof d[k] === 'object') {
            rows.push([labels[k], moeda(d[k].atual), moeda(d[k].anterior)]);
        }
    });
    H += tab(['Conta','Período Atual','Período Anterior'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }

// ===== 3. ANÁLISE BO (atual + anterior) =====
H += tit(3, 'Análise do Balanço Orçamentário');
H += '<div class="desc">Comparativo das receitas e despesas orçamentárias.</div>';
if (D.analise_orcamentaria) {
    const d = D.analise_orcamentaria;
    const rows = [];
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
    campos.forEach(([label, key]) => {
        const at = d.atual ? d.atual[key] : null;
        const an = d.anterior ? d.anterior[key] : null;
        rows.push([label, moeda(at), moeda(an)]);
    });
    H += tab(['Indicador','Período Atual','Período Anterior'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }

// ===== 4. ANÁLISE BF (todas as linhas) =====
H += tit(4, 'Análise do Balanço Financeiro');
H += '<div class="desc">Movimentação financeira consolidada (receitas, despesas, extraorçamentário, caixa).</div>';
if (D.analise_financeira_bf) {
    const d = D.analise_financeira_bf;
    const blocos = [
        ['Receitas', d.receitas],
        ['Despesas', d.despesas],
        ['Extraorçamentário', d.extra],
        ['Caixa', d.caixa]
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
if (D.analise_dfc && D.analise_dfc.dados) {
    const d = D.analise_dfc.dados;
    const blocos = [
        ['Fluxo Operacional', d.operacional],
        ['Fluxo de Investimento', d.investimento],
        ['Fluxo de Financiamento', d.financiamento],
        ['Apuração de Caixa', d.caixa]
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
if (D.analise_patrimonial) {
    const d = D.analise_patrimonial;
    const rows = [];
    const labels = {
        variacoes_ativas:'Variações Ativas (VPA)', transf_recebidas:'Transferências Recebidas',
        reversao_provisoes:'Reversão de Provisões', variacoes_diminutivas:'Variações Diminutivas (VPD)',
        pessoal_encargos:'Pessoal e Encargos', servicos_terceiros:'Serviços de Terceiros',
        transf_concedidas:'Transferências Concedidas', superavit_patrimonial:'Superávit Patrimonial',
        margem_patrimonial:'Margem Patrimonial (%)'
    };
    Object.keys(labels).forEach(k => {
        if (d[k] && typeof d[k] === 'object') {
            const at = d[k].atual;
            const an = d[k].anterior;
            if (k === 'margem_patrimonial') {
                rows.push([labels[k], pct(at), pct(an)]);
            } else {
                rows.push([labels[k], moeda(at), moeda(an)]);
            }
        }
    });
    H += tab(['Item','Atual','Anterior'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }

// ===== 7. COMPARATIVO DE RECEITAS (grupos + cores) =====
H += tit(7, 'Comparativo de Receitas');
H += '<div class="desc">Comparativo consolidado de receitas (grupos + CORENs).</div>';
if (D.comparativo_receitas) {
    const d = D.comparativo_receitas;
    const at = d.atual || {};
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

// ===== 8. COMPARATIVO DE DESPESAS (grupos + detalhes) =====
H += tit(8, 'Comparativo de Despesas');
H += '<div class="desc">Comparativo consolidado de despesas (grupos + detalhes).</div>';
if (D.comparativo_despesas) {
    const d = D.comparativo_despesas;
    const at = d.atual || {};
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
if (D.liquidez) {
    const d = D.liquidez;
    H += sub('Liquidez');
    const rowsLiq = [];
    if (d.liquidez) {
        [['Liquidez Imediata','liquidez_imediata'], ['Liquidez Corrente','liquidez_corrente'],
         ['Liquidez Seca','liquidez_seca'], ['Liquidez Geral','liquidez_geral']].forEach(([label, key]) => {
            if (d.liquidez[key] !== undefined) rowsLiq.push([label, d.liquidez[key]]);
        });
    }
    H += tab(['Indicador','Valor'], rowsLiq);
    
    if (d.estrutura) {
        H += sub('Estrutura Patrimonial');
        const rowsEst = [];
        [['Endividamento Geral','endividamento_geral'], ['Part. Capital de Terceiros','part_capital_terceiros'],
         ['Imobilização do PL','imobilizacao_pl']].forEach(([label, key]) => {
            if (d.estrutura[key] !== undefined) rowsEst.push([label, d.estrutura[key] + '%']);
        });
        H += tab(['Indicador','Valor'], rowsEst);
    }
    
    if (d.valores) {
        H += sub('Valores Base');
        const rowsVal = [];
        const labelsVal = { caixa:'Caixa', ativo_circulante:'Ativo Circulante', estoques:'Estoques',
            realizavel_lp:'Realizável LP', ativo_nao_circulante:'Ativo Não Circulante',
            imobilizado:'Imobilizado', passivo_circulante:'Passivo Circulante',
            passivo_nao_circulante:'Passivo Não Circulante', passivo_total:'Passivo Total',
            ativo_total:'Ativo Total', patrimonio_liquido:'Patrimônio Líquido' };
        Object.keys(labelsVal).forEach(k => {
            if (d.valores[k] !== undefined) rowsVal.push([labelsVal[k], moeda(d.valores[k])]);
        });
        H += tab(['Item','Valor'], rowsVal);
    }
} else { H += '<p>Módulo não encontrado.</p>'; }

// ===== 10. PANORAMA =====
H += tit(10, 'Panorama de Resultados');
H += '<div class="desc">Resumo executivo dos principais indicadores.</div>';
if (D.panorama) {
    const d = D.panorama;
    const labels = {
        ativo_total:'Ativo Total', passivo_total:'Passivo Total', patrimonio_liquido:'Patrimônio Líquido',
        caixa_bp:'Caixa e Equivalentes', receita_realizada:'Receitas Realizadas',
        despesa_empenhada:'Despesas Empenhadas', superavit_orcamentario:'Resultado Orçamentário',
        superavit_patrimonial:'Superávit Patrimonial', superavit_financeiro:'Superávit Financeiro'
    };
    const rows = [];
    Object.keys(labels).forEach(k => {
        if (d[k] !== undefined) rows.push([labels[k], moeda(d[k])]);
    });
    H += tab(['Indicador','Valor'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }

// ===== 11. CENTRO DE CUSTOS (todos os centros) =====
H += tit(11, 'Análise por Centro de Custos');
H += '<div class="desc">Distribuição das despesas por centro de custo (atual x anterior).</div>';
if (D.centro_custos && D.centro_custos.centros) {
    const at = D.centro_custos.centros || [];
    const an = D.centro_custos.centros_anterior || [];
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

// ===== 12. CUSTO DE PESSOAL (todos os campos) =====
H += tit(12, 'Custo de Pessoal');
H += '<div class="desc">Custo de pessoal x limite legal (Resolução Cofen 814/2026).</div>';
if (D.custo_pessoal) {
    const d = D.custo_pessoal;
    H += sub('Composição do Custo');
    H += tab(['Item','Atual','Anterior','Total'], [
        ['Pessoal e Encargos', moeda(d.pessoal_atual), moeda(d.pessoal_anterior), moeda(d.pessoal_total)],
        ['Outras Despesas Variáveis', moeda(d.outras_atual), moeda(d.outras_anterior), moeda(d.outras_total)],
        ['Terceirização', moeda(d.terc_atual), moeda(d.terc_anterior), moeda(d.terc_total)],
        ['CUSTO TOTAL (Bruto)', moeda(d.custo_atual), moeda(d.custo_anterior), moeda(d.custo_total)],
        ['RCL Total (12 meses)', moeda(d.rcl_atual), moeda(d.rcl_anterior), moeda(d.rcl_total)]
    ]);
    H += sub('Limite e Margem');
    H += tab(['Item','Valor'], [
        ['Limite Resolução Cofen 814/2026', moeda(d.limite_total)],
        ['Margem Disponível', moeda(d.margem_disponivel_total)],
        ['% Custo sobre RCL', pct(d.pct_custo_total)],
        ['Faixa de Controle', d.faixa_controle || '-']
    ]);
} else { H += '<p>Módulo não encontrado.</p>'; }

document.getElementById('conteudo').innerHTML = H;
</script>
</body>
</html>"""

with open("pc_frontend/relatorio_consolidado_template.html", "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Template HTML completo criado.")
