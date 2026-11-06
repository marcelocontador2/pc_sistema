arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

# Localiza o bloco 11 (Análise por Centro de Custos)
padrao = re.compile(
    r"(//\s*11\.\s*ANÁLISE\s+POR\s+CENTRO\s+DE\s+CUSTOS.*?)(?=\n\s*//\s*12\.|\Z)",
    re.DOTALL | re.IGNORECASE
)
m = padrao.search(html)
if not m:
    print("[ERRO] Bloco 11 não encontrado.")
    raise SystemExit

bloco_original = m.group(0)

# 1. Remove a nota (destaque) que foi adicionada no script anterior
bloco_original = re.sub(r"// --- Destaque Maior Gasto ---.*?H \+= '</div>';", "", bloco_original, flags=re.DOTALL)

# 2. Lógica para criar a tabela de ranking (ordem decrescente)
logica_ranking = """
    // --- Tabela de Ranking (Ordem Decrescente) ---
    if (rows && rows.length > 1) {
        // Cria uma cópia das linhas (sem a linha TOTAL) para ordenar
        const ranking = rows.slice(0, -1).map(r => {
            // Converte a string formatada 'R$ 16.937.035,31' de volta para número para ordenar
            const strValor = r[1].replace('R$ ', '').replace(/\\./g, '').replace(',', '.');
            return {
                nome: r[0],
                valorStr: r[1],
                valorNum: parseFloat(strValor),
                percStr: r[3] // A variação percentual
            };
        });

        // Ordena do maior para o menor
        ranking.sort((a, b) => b.valorNum - a.valorNum);

        // Adiciona a nova tabela
        H += sub('Ranking de Gastos (Maior para Menor)');
        
        const rowsRanking = ranking.map((r, index) => {
            return [String(index + 1), r.nome, r.valorStr, r.percStr];
        });

        H += tab(['#', 'Centro de Custo', 'Gasto Atual', 'Variação (%)'], rowsRanking);
    }
"""

# 3. Insere a lógica logo após a renderização da tabela original
# (após o H += tab(...) que monta a tabela principal)
match_tab = re.search(r"(H\s*\+=\s*tab\(\[.*?\],\s*rows\);)", bloco_original)
if match_tab:
    bloco_ajustado = bloco_original.replace(
        match_tab.group(1),
        match_tab.group(1) + "\n" + logica_ranking
    )
else:
    # Fallback
    idx = bloco_original.rfind('}')
    bloco_ajustado = bloco_original[:idx] + logica_ranking + bloco_original[idx:]

html = html.replace(bloco_original, bloco_ajustado)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Tabela de ranking decrescente adicionada abaixo da original.")
