arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re
import shutil

# 1. Cria backup de segurança antes de mexer
shutil.copy(arq, arq + ".bak_seguranca")
print("Backup de segurança criado.")

# 2. Localiza a Seção 2 atual
padrao = re.compile(r"(// ===== 2\. ANÁLISE BP =====.*?)(?=\n// ===== 3\.)", re.DOTALL)
m = padrao.search(html)

if not m:
    print("[ERRO] Não achei a seção 2 no arquivo.")
    raise SystemExit

bloco_antigo = m.group(1)

# 3. Novo bloco: Busca genérica e renderização à prova de falhas
novo_bloco = """// ===== 2. ANÁLISE BP =====
H += tit(2, 'Análise do Balanço Patrimonial');
H += '<div class="desc">Comparativo das contas do Balanço Patrimonial (período atual x anterior).</div>';
try {
    // Tenta pegar o objeto de todas as formas possíveis
    let bp = unwrap(D.analise_bp) || D.balanco_patrimonial || D.bp || null;
    
    if (bp) {
        const rows = [];
        const labels = {
            ativo_circulante:'Ativo Circulante', caixa:'Caixa e Equivalentes',
            creditos:'Créditos a Curto Prazo', ativo_nao_circulante:'Ativo Não Circulante',
            ativo_realizavel:'Ativo Realizável a Longo Prazo', imobilizado:'Imobilizado',
            total_ativo:'TOTAL DO ATIVO', passivo_circulante:'Passivo Circulante',
            passivo_nao_circulante:'Passivo Não Circulante', passivo_total:'Passivo Total',
            patrimonio_liquido:'Patrimônio Líquido', total_passivo:'TOTAL DO PASSIVO'
        };

        // Varre o objeto para encontrar os valores, ignorando maiúsculas/minúsculas
        const bpLower = {};
        Object.keys(bp).forEach(k => { bpLower[k.toLowerCase()] = bp[k]; });

        Object.keys(labels).forEach(k => {
            if (bpLower[k] !== undefined) {
                const item = bpLower[k];
                if (typeof item === 'object' && item !== null) {
                    const at = item.atual !== undefined ? item.atual : 0;
                    const an = item.anterior !== undefined ? item.anterior : 0;
                    rows.push([labels[k], moeda(at), moeda(an), varPct(at, an)]);
                } else if (!isNaN(item)) {
                    rows.push([labels[k], moeda(item), moeda(0), varPct(item, 0)]);
                }
            }
        });
        
        if (rows.length > 0) {
            H += tab(['Conta','Período Atual','Período Anterior', 'Var. (%)'], rows);
        } else {
            // Se não achou nenhuma chave conhecida, cospe o debug na tela
            H += '<div style="border: 2px solid red; padding: 10px; background: #fff; color: black; font-size: 10px;">';
            H += '<b>DEBUG: Dados não mapeados. Chaves disponíveis no JSON:</b><br>';
            H += Object.keys(bp).join(', ');
            H += '<br><br><b>Conteúdo:</b><br><pre>' + JSON.stringify(bp, null, 2).substring(0, 1000) + '</pre>';
            H += '</div>';
        }
    } else {
        H += '<p>Módulo não encontrado no JSON.</p>';
    }
} catch (e) {
    H += '<p style="color:red;">Erro ao renderizar: ' + e.message + '</p>';
}
"""

html = html.replace(bloco_antigo, novo_bloco)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Seção 2 reescrita com varredura genérica e debug visual.")
