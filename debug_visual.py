arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

# Remove qualquer debug antigo
html = re.sub(r"<script>\s*document\.addEventListener\('DOMContentLoaded'.*?</script>", "", html, flags=re.DOTALL)
html = re.sub(r"// DEBUG: mostrar estrutura.*?\}", "", html, flags=re.DOTALL)

# Localiza o bloco 7
padrao = re.compile(
    r"(//\s*7\.\s*COMPARATIVO\s+DE\s+RECEITAS.*?)(?=\n\s*//\s*8\.|\Z)",
    re.DOTALL | re.IGNORECASE
)
m = padrao.search(html)
if not m:
    print("[ERRO] Bloco 7 não encontrado.")
    raise SystemExit

bloco_original = m.group(0)

# Este bloco vai cuspir os dados na tela para podermos ver
novo_bloco = """// 7. COMPARATIVO DE RECEITAS
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
        H += tab(['Grupo','Orçado','Realizado','%'],
            at.grupos.map(g => [g.nome, moeda(g.orcado), moeda(g.realizado), pct(g.percentual)]));
    }

    // ===== DEBUG VISUAL =====
    if (at.cores && at.cores.length) {
        H += '<div style="border:2px solid red; padding:10px; margin:10px 0; font-family:monospace; font-size:11px; background:#fff;">';
        H += '<b style="color:red;">DEBUG - ESTRUTURA DA PRIMEIRA COREN:</b><br>';
        H += '<pre>' + JSON.stringify(at.cores[0], null, 2) + '</pre>';
        H += '<b style="color:red;">CHAVES DISPONÍVEIS:</b><br>';
        H += '<pre>' + Object.keys(at.cores[0]).join(', ') + '</pre>';
        H += '</div>';
    }
    // ===== FIM DEBUG =====

    // --- Consolidado por Regional ---
    if (at.cores && at.cores.length) {
        const mapa = new Map();
        at.cores.forEach(c => {
            // AQUI VAMOS AJUSTAR O CAMPO CORRETO APÓS VER O DEBUG
            const key = (
                c.regional || c.nome_regional || c.regiao || c.Regional || 'NÃO INFORMADO'
            ).toString().trim().toUpperCase();
            const orc = Number(c.orcado || 0);
            const real = Number(c.realizado || 0);
            if (!mapa.has(key)) mapa.set(key, { regional: key, orcado: 0, realizado: 0 });
            const item = mapa.get(key);
            item.orcado += orc;
            item.realizado += real;
        });
        const rows = [];
        [...mapa.values()]
            .sort((a, b) => b.realizado - a.realizado)
            .forEach(item => {
                const perc = item.orcado ? (item.realizado / item.orcado * 100) : 0;
                rows.push([item.regional, moeda(item.orcado), moeda(item.realizado), pct(perc)]);
            });
        H += sub('Desdobramento por Regional');
        H += tab(['Regional','Orçado','Realizado','%'], rows);
    }
} else { H += '<p>Módulo não encontrado.</p>'; }
"""

html = html.replace(bloco_original, novo_bloco)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Bloco 7 modificado com DEBUG VISUAL em vermelho.")
