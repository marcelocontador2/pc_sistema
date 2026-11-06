arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

padrao = re.compile(
    r"(// 6\. ANÁLISE DVP.*?H \+= tab\(\['Item','Atual','Anterior'\], rows\);.*?\} else \{ H \+= '<p>Módulo não encontrado\.</p>'; \})",
    re.DOTALL
)

nova_secao = '''// 6. ANÁLISE DVP
H += tit(6, 'Análise das Variações Patrimoniais');
H += '<div class="desc">Demonstração das Variações Patrimoniais.</div>';
const dvp = unwrap(D.analise_patrimonial);
if (dvp) {
    const labels = {
        variacoes_ativas:'Variações Ativas (VPA)',
        transf_recebidas:'Transferências Recebidas',
        reversao_provisoes:'Reversão de Provisões',
        variacoes_diminutivas:'Variações Diminutivas (VPD)',
        pessoal_encargos:'Pessoal e Encargos',
        servicos_terceiros:'Serviços de Terceiros',
        transf_concedidas:'Transferências Concedidas',
        superavit_patrimonial:'Superávit Patrimonial',
        margem_patrimonial:'Margem Patrimonial (%)'
    };
    const rows = [];
    Object.keys(labels).forEach(k => {
        if (dvp[k] && typeof dvp[k] === 'object') {
            const at = dvp[k].atual;
            const an = dvp[k].anterior;
            let fAt, fAn;
            if (k === 'margem_patrimonial') {
                fAt = pct(at);
                fAn = pct(an);
            } else {
                fAt = moeda(at);
                fAn = moeda(an);
            }
            // Margem patrimonial não tem variação percentual (é ela mesma um %)
            const varStr = (k === 'margem_patrimonial') ? '-' : varPct(at, an);
            rows.push([labels[k], fAt, fAn, varStr]);
        }
    });
    H += tab(['Item','Atual','Anterior','Var. (%)'], rows);
} else { H += '<p>Módulo não encontrado.</p>'; }'''

if padrao.search(html):
    html = padrao.sub(lambda m: nova_secao, html)
    with open(arq, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Seção da DVP atualizada (com coluna Var. % e margem formatada corretamente).")
else:
    print("[ERRO] Não encontrei o bloco da DVP no template.")
