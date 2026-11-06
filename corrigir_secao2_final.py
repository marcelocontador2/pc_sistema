arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

# O bloco atual que está no arquivo
bloco_atual = """// ===== 2. ANÁLISE BP =====
H += tit(2, 'Análise do Balanço Patrimonial');
H += '<div class="desc">Comparativo das contas do Balanço Patrimonial.</div>';
const bp = unwrap(D.analise_bp);
if (bp) {
    const rows = [];
    ['ativo_circulante','caixa','creditos','ativo_nao_circulante','ativo_realizavel','imobilizado','total_ativo','passivo_circulante','passivo_nao_circulante','passivo_total','patrimonio_liquido','total_passivo'].forEach(k => {
        if (bp[k]) rows.push([k.replace(/_/g,' ').toUpperCase(), moeda(bp[k].atual), moeda(bp[k].anterior)]);
    });
    H += tab(['Conta','Período Atual','Período Anterior'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }"""

# O novo bloco, à prova de falhas de maiúsculas/minúsculas e com variação
bloco_novo = """// ===== 2. ANÁLISE BP =====
H += tit(2, 'Análise do Balanço Patrimonial');
H += '<div class="desc">Comparativo das contas do Balanço Patrimonial (período atual x anterior).</div>';
const bp = unwrap(D.analise_bp);
if (bp) {
    // Normaliza as chaves para minúsculas para evitar erro se o backend mandar MAIÚSCULO
    const bpLower = {};
    Object.keys(bp).forEach(k => { bpLower[k.toLowerCase()] = bp[k]; });
    
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
        if (bpLower[k] !== undefined) {
            const item = bpLower[k];
            // Se for um objeto (ex: {atual: 100, anterior: 50})
            if (typeof item === 'object' && item !== null) {
                const at = item.atual !== undefined ? item.atual : 0;
                const an = item.anterior !== undefined ? item.anterior : 0;
                rows.push([labels[k], moeda(at), moeda(an), varPct(at, an)]);
            } 
            // Se for um valor direto (ex: 100)
            else if (!isNaN(item)) {
                rows.push([labels[k], moeda(item), moeda(0), varPct(item, 0)]);
            }
        }
    });
    H += tab(['Conta','Período Atual','Período Anterior', 'Var. (%)'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }"""

if bloco_atual in html:
    html = html.replace(bloco_atual, bloco_novo)
    with open(arq, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Seção 2 corrigida com sucesso!")
else:
    print("[AVISO] Texto exato não encontrado. Tentando substituição via regex...")
    padrao = re.compile(r"(// ===== 2\. ANÁLISE BP =====.*?)(?=\n// ===== 3\.)", re.DOTALL)
    m = padrao.search(html)
    if m:
        html = html.replace(m.group(1), bloco_novo)
        with open(arq, "w", encoding="utf-8") as f:
            f.write(html)
        print("[OK] Seção 2 corrigida via regex!")
    else:
        print("[ERRO] Não foi possível encontrar a Seção 2.")
