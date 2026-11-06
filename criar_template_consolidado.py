import os

# =========================================================
# 1. Cria o template HTML
# =========================================================
html_template = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Relatório Consolidado</title>
<style>
    @page { size: A4 portrait; margin: 15mm; }
    body { font-family: 'Segoe UI', Arial, sans-serif; color: #333; line-height: 1.4; margin: 0; }
    
    /* ===== CAPA ===== */
    .capa { text-align: center; padding-top: 70mm; page-break-after: always; }
    .capa .faixa { background: #003366; color: white; padding: 50px 0; margin: -15mm -15mm 40px -15mm; }
    .capa h1 { color: white; margin: 0; font-size: 32px; letter-spacing: 4px; font-weight: bold; }
    .capa h2 { color: white; margin: 10px 0 0 0; font-size: 16px; font-weight: normal; }
    .capa .entidade { font-size: 16px; color: #555; margin: 40px 0 30px 0; }
    .capa .info { background: #f4f6f9; border-left: 5px solid #0056b3; padding: 20px; margin: 20px auto; max-width: 400px; }
    .capa .info .label { font-size: 11px; color: #666; letter-spacing: 1px; }
    .capa .info .valor { font-size: 22px; font-weight: bold; color: #003366; margin-top: 5px; }
    .capa .rodape { color: #999; font-size: 11px; margin-top: 80px; }
    
    /* ===== SEÇÕES ===== */
    h2.secao-titulo { 
        color: #003366; 
        border-bottom: 3px solid #003366; 
        padding-bottom: 8px; 
        page-break-before: always;
        font-size: 22px;
        margin-bottom: 20px;
    }
    
    /* ===== TABELAS ===== */
    table.tabela { width: 100%; border-collapse: collapse; margin: 15px 0; page-break-inside: auto; }
    table.tabela th { 
        background: #003366; 
        color: white; 
        padding: 10px; 
        text-align: left; 
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    table.tabela td { 
        padding: 8px 10px; 
        border-bottom: 1px solid #ddd; 
        font-size: 12px; 
    }
    table.tabela td.right { text-align: right; }
    table.tabela tr:nth-child(even) { background: #f8f9fa; }
    
    /* ===== CARDS ===== */
    .card-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }
    .card { 
        background: #f4f6f9; 
        padding: 20px; 
        border-radius: 8px; 
        border-left: 5px solid #0056b3; 
    }
    .card .label { font-size: 10px; color: #666; text-transform: uppercase; letter-spacing: 1px; }
    .card .valor { font-size: 22px; font-weight: bold; color: #003366; margin-top: 8px; }
    
    /* ===== STATUS ===== */
    .status-ok { background: #d4edda; border-left: 5px solid #28a745; padding: 20px; margin: 20px 0; border-radius: 6px; }
    .status-ok strong { color: #155724; font-size: 16px; }
    .status-ok p { color: #155724; margin: 10px 0 0 0; }
    .status-warn { background: #fff3cd; border-left: 5px solid #ffc107; padding: 20px; margin: 20px 0; border-radius: 6px; }
    .status-warn strong { color: #856404; font-size: 16px; }
    .status-erro { background: #f8d7da; border-left: 5px solid #dc3545; padding: 20px; margin: 20px 0; border-radius: 6px; }
    
    /* ===== DESCRIÇÃO SEÇÃO ===== */
    .secao-desc { font-size: 12px; color: #666; margin-bottom: 15px; font-style: italic; }
    
    /* ===== RODAPÉ DAS PÁGINAS ===== */
    .rodape-pagina { 
        position: fixed; 
        bottom: -10mm; 
        left: 0; 
        right: 0; 
        text-align: center; 
        font-size: 9px; 
        color: #999; 
    }
</style>
</head>
<body>

<!-- ===== CAPA ===== -->
<div class="capa">
    <div class="faixa">
        <h1>RELATÓRIO CONSOLIDADO</h1>
        <h2>Análise Contábil</h2>
    </div>
    <div class="entidade">COFEN - Conselho Federal de Enfermagem</div>
    <div class="info">
        <div class="label">PERÍODO DE ANÁLISE</div>
        <div class="valor">{periodo}</div>
    </div>
    <div class="rodape">
        Gerado em: {data_geracao}<br>
        SGPC - Sistema de Gestão de Prestação de Contas
    </div>
</div>

<!-- ===== CONTEÚDO (preenchido via JS) ===== -->
<div id="conteudo"></div>

<script>
const DADOS = {dados_json};

function fmtMoeda(v) {
    if (v === null || v === undefined || isNaN(v)) return 'R$ 0,00';
    v = parseFloat(v);
    if (Math.abs(v) >= 1000000) {
        return 'R$ ' + (v/1000000).toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + ' mi';
    }
    return 'R$ ' + v.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
}

function fmtPct(v) {
    if (v === null || v === undefined) return '0,00%';
    return parseFloat(v).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%';
}

function titulo(num, titulo) {
    return '<h2 class="secao-titulo">' + num + '. ' + titulo + '</h2>';
}

function naoEncontrado() {
    return '<div class="status-warn"><strong>⚠ Módulo não encontrado neste histórico.</strong></div>';
}

function renderTabela(headers, rows) {
    let html = '<table class="tabela"><thead><tr>';
    headers.forEach(h => { html += '<th>' + h + '</th>'; });
    html += '</tr></thead><tbody>';
    rows.forEach(row => {
        html += '<tr>';
        row.forEach((cell, i) => {
            html += '<td' + (i > 0 ? ' class="right"' : '') + '>' + cell + '</td>';
        });
        html += '</tr>';
    });
    html += '</tbody></table>';
    return html;
}

function renderCards(items) {
    let html = '<div class="card-grid">';
    items.forEach(item => {
        html += '<div class="card"><div class="label">' + item.label + '</div><div class="valor">' + item.valor + '</div></div>';
    });
    html += '</div>';
    return html;
}

// ============ RENDERIZA CADA SEÇÃO ============

let html = '';

// 1. INTEGRIDADE
html += titulo(1, 'Integridade entre Demonstrações');
if (DADOS.integridade) {
    html += '<div class="status-ok"><strong>✓ Integridade Verificada com Sucesso</strong>';
    html += '<p>O sistema realizou a verificação de integridade entre todas as demonstrações contábeis do período.</p>';
    html += '<p>Total de Verificações: <strong>' + (DADOS.integridade.total || 'N/A') + '</strong> | OK: <strong>' + (DADOS.integridade.ok || 'N/A') + '</strong></p></div>';
} else { html += naoEncontrado(); }

// 2. ANÁLISE BP
html += titulo(2, 'Análise do Balanço Patrimonial');
html += '<div class="secao-desc">Comparativo entre período atual e período anterior das contas do Balanço Patrimonial.</div>';
if (DADOS.analise_bp && DADOS.analise_bp.dados) {
    const d = DADOS.analise_bp.dados.dados || DADOS.analise_bp.dados;
    const rows = [];
    Object.keys(d).forEach(k => {
        const v = d[k];
        if (v && typeof v === 'object' && 'atual' in v) {
            rows.push([k.replace(/_/g, ' ').toUpperCase(), fmtMoeda(v.atual), fmtMoeda(v.anterior)]);
        }
    });
    html += renderTabela(['Conta', 'Período Atual', 'Período Anterior'], rows);
} else { html += naoEncontrado(); }

// 3. ANÁLISE BO
html += titulo(3, 'Análise do Balanço Orçamentário');
html += '<div class="secao-desc">Comparativo das receitas e despesas orçamentárias do período.</div>';
if (DADOS.analise_orcamentaria && DADOS.analise_orcamentaria.dados) {
    const d = DADOS.analise_orcamentaria.dados.dados || DADOS.analise_orcamentaria.dados;
    const rows = [];
    Object.keys(d).forEach(k => {
        const v = d[k];
        if (typeof v === 'number' || typeof v === 'string') {
            rows.push([k.replace(/_/g, ' ').toUpperCase(), fmtMoeda(v)]);
        }
    });
    html += renderTabela(['Item', 'Valor'], rows);
} else { html += naoEncontrado(); }

// 4. ANÁLISE BF
html += titulo(4, 'Análise do Balanço Financeiro');
html += '<div class="secao-desc">Movimentação financeira consolidada do período.</div>';
if (DADOS.analise_financeira_bf && DADOS.analise_financeira_bf.dados) {
    const d = DADOS.analise_financeira_bf.dados.dados || DADOS.analise_financeira_bf.dados;
    const rows = [];
    Object.keys(d).forEach(k => {
        const v = d[k];
        if (typeof v === 'number' || typeof v === 'string') {
            rows.push([k.replace(/_/g, ' ').toUpperCase(), fmtMoeda(v)]);
        }
    });
    html += renderTabela(['Item', 'Valor'], rows);
} else { html += naoEncontrado(); }

// 5. ANÁLISE DFC
html += titulo(5, 'Análise do Fluxo de Caixa');
html += '<div class="secao-desc">Demonstração do Fluxo de Caixa do período.</div>';
if (DADOS.analise_dfc && DADOS.analise_dfc.dados) {
    const d = DADOS.analise_dfc.dados.dados || DADOS.analise_dfc.dados;
    const rows = [];
    Object.keys(d).forEach(k => {
        const v = d[k];
        if (typeof v === 'number' || typeof v === 'string') {
            rows.push([k.replace(/_/g, ' ').toUpperCase(), fmtMoeda(v)]);
        }
    });
    html += renderTabela(['Item', 'Valor'], rows);
} else { html += naoEncontrado(); }

// 6. ANÁLISE DVP
html += titulo(6, 'Análise das Variações Patrimoniais');
html += '<div class="secao-desc">Demonstração das Variações Patrimoniais do período.</div>';
if (DADOS.analise_patrimonial && DADOS.analise_patrimonial.dados) {
    const d = DADOS.analise_patrimonial.dados.dados || DADOS.analise_patrimonial.dados;
    const rows = [];
    Object.keys(d).forEach(k => {
        const v = d[k];
        if (typeof v === 'number' || typeof v === 'string') {
            rows.push([k.replace(/_/g, ' ').toUpperCase(), fmtMoeda(v)]);
        }
    });
    html += renderTabela(['Item', 'Valor'], rows);
} else { html += naoEncontrado(); }

// 7. COMPARATIVO DE RECEITAS
html += titulo(7, 'Comparativo de Receitas');
html += '<div class="secao-desc">Comparativo consolidado de receitas entre período atual e anterior.</div>';
if (DADOS.comparativo_receitas && DADOS.comparativo_receitas.dados) {
    const d = DADOS.comparativo_receitas.dados.dados || DADOS.comparativo_receitas.dados;
    const atual = d.atual || {};
    html += renderCards([
        {label: 'Receita Orçada', valor: fmtMoeda(atual.orcado_total)},
        {label: 'Receita Realizada', valor: fmtMoeda(atual.realizado_total)},
        {label: '% Execução', valor: fmtPct(atual.percentual_total)}
    ]);
} else { html += naoEncontrado(); }

// 8. COMPARATIVO DE DESPESAS
html += titulo(8, 'Comparativo de Despesas');
html += '<div class="secao-desc">Comparativo consolidado de despesas entre período atual e anterior.</div>';
if (DADOS.comparativo_despesas && DADOS.comparativo_despesas.dados) {
    const d = DADOS.comparativo_despesas.dados.dados || DADOS.comparativo_despesas.dados;
    const atual = d.atual || {};
    html += renderCards([
        {label: 'Despesa Orçada', valor: fmtMoeda(atual.orcado_total)},
        {label: 'Despesa Empenhada', valor: fmtMoeda(atual.empenhado_total)},
        {label: '% Execução', valor: fmtPct(atual.percentual_total)}
    ]);
} else { html += naoEncontrado(); }

// 9. ÍNDICES DE LIQUIDEZ
html += titulo(9, 'Índices de Liquidez');
html += '<div class="secao-desc">Indicadores de liquidez imediata, corrente, seca e geral.</div>';
if (DADOS.liquidez && DADOS.liquidez.dados) {
    const d = DADOS.liquidez.dados.dados || DADOS.liquidez.dados;
    const liq = d.liquidez || d;
    const rows = [];
    [['liquidez_imediata','Liquidez Imediata'], ['liquidez_corrente','Liquidez Corrente'], ['liquidez_seca','Liquidez Seca'], ['liquidez_geral','Liquidez Geral']].forEach(([k, label]) => {
        if (liq[k] !== undefined) rows.push([label, liq[k]]);
    });
    html += renderTabela(['Indicador', 'Valor'], rows);
} else { html += naoEncontrado(); }

// 10. PANORAMA
html += titulo(10, 'Panorama de Resultados');
html += '<div class="secao-desc">Resumo executivo dos principais indicadores contábeis e orçamentários.</div>';
if (DADOS.panorama && DADOS.panorama.dados) {
    const d = DADOS.panorama.dados.dados || DADOS.panorama.dados;
    html += renderCards([
        {label: 'Ativo Total', valor: fmtMoeda(d.ativo_total)},
        {label: 'Passivo Total', valor: fmtMoeda(d.passivo_total)},
        {label: 'Patrimônio Líquido', valor: fmtMoeda(d.patrimonio_liquido)},
        {label: 'Caixa e Equivalentes', valor: fmtMoeda(d.caixa_bp)},
        {label: 'Receitas Realizadas', valor: fmtMoeda(d.receita_realizada)},
        {label: 'Despesas Empenhadas', valor: fmtMoeda(d.despesa_empenhada)},
        {label: 'Resultado Orçamentário', valor: fmtMoeda(d.superavit_orcamentario)},
        {label: 'Superávit Patrimonial', valor: fmtMoeda(d.superavit_patrimonial)},
        {label: 'Superávit Financeiro', valor: fmtMoeda(d.superavit_financeiro)}
    ]);
} else { html += naoEncontrado(); }

// 11. CENTRO DE CUSTOS
html += titulo(11, 'Análise por Centro de Custos');
html += '<div class="secao-desc">Distribuição das despesas por centro de custo.</div>';
if (DADOS.centro_custos && DADOS.centro_custos.dados) {
    const d = DADOS.centro_custos.dados.dados || DADOS.centro_custos.dados;
    const rows = [];
    Object.keys(d).forEach(k => {
        const v = d[k];
        if (typeof v === 'number' || typeof v === 'string') {
            rows.push([k.replace(/_/g, ' ').toUpperCase(), fmtMoeda(v)]);
        }
    });
    html += renderTabela(['Centro de Custo', 'Valor'], rows);
} else { html += naoEncontrado(); }

// 12. CUSTO DE PESSOAL
html += titulo(12, 'Custo de Pessoal');
html += '<div class="secao-desc">Análise do custo de pessoal x limite legal (Resolução Cofen 814/2026).</div>';
if (DADOS.custo_pessoal && DADOS.custo_pessoal.dados) {
    const d = DADOS.custo_pessoal.dados.dados || DADOS.custo_pessoal.dados;
    html += renderCards([
        {label: 'RCL Total (12 meses)', valor: fmtMoeda(d.rcl_total)},
        {label: 'Custo Total', valor: fmtMoeda(d.custo_total)},
        {label: 'Limite Legal', valor: fmtMoeda(d.limite_total)},
        {label: 'Margem Disponível', valor: fmtMoeda(d.margem_disponivel_total)},
        {label: 'Custo de Pessoal', valor: fmtMoeda(d.pessoal_total)},
        {label: '% de Custo sobre RCL', valor: fmtPct(d.pct_custo_total)}
    ]);
} else { html += naoEncontrado(); }

document.getElementById('conteudo').innerHTML = html;
</script>
</body>
</html>"""

# =========================================================
# 2. Salva o template
# =========================================================
arq_template = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq_template, "w", encoding="utf-8") as f:
    f.write(html_template)
print(f"[OK] Template HTML criado: {arq_template}")
