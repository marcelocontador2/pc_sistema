arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

# 1. Limpa tentativas anteriores (incluindo o script JS visual e tentativas antigas)
html = re.sub(r"<script>\s*document\.addEventListener\('DOMContentLoaded'.*?</script>", "", html, flags=re.DOTALL)
html = re.sub(r"// --- Tabela de Ranking \(Ordem Decrescente\) ---.*?H \+= tab\(\['#', 'Centro de Custo', 'Gasto Atual', 'Variação \(%\)'\], rowsRanking\);", "", html, flags=re.DOTALL)
html = re.sub(r"// --- Destaque Maior Gasto ---.*?H \+= '</div>';", "", html, flags=re.DOTALL)

# 2. Localiza a Seção 11 pela sua chamada de título
# O padrão busca desde "tit(11" até o próximo título (tit(12, ...) ou fim)
padrao_secao11 = re.compile(
    r"(H\s*\+=\s*tit\(11,\s*['\"]Análise por Centro de Custos['\"]\);.*?)(?=H\s*\+=\s*tit\(12,|\Z)",
    re.DOTALL | re.IGNORECASE
)
m = padrao_secao11.search(html)
if not m:
    print("[ERRO] Seção 11 não encontrada pelo título 'Análise por Centro de Custos'.")
    raise SystemExit

bloco_secao11 = m.group(0)
print("--- Início da Seção 11 localizada ---")
print(bloco_secao11[:250] + "...")
print("-------------------------------------")

# 3. Encontra a chamada da tabela original dentro da seção 11
# Geralmente é algo como: H += tab(['CENTRO DE CUSTO', 'ATUAL', ...], rows);
match_tab = re.search(r"(H\s*\+=\s*tab\(\[[^\]]+\],\s*[a-zA-Z0-9_]+\);)", bloco_secao11)

if not match_tab:
    print("[ERRO] Não encontrei a renderização da tabela (H += tab(...)) dentro da seção 11.")
    raise SystemExit

chamada_tabela = match_tab.group(1)
print("--- Chamada de tabela localizada: ---")
print(chamada_tabela)
print("-------------------------------------")

# 4. Cria o código para a tabela de ranking
# A lógica vai inserir uma nova tabela logo após a original
codigo_ranking = """
    // --- Ranking de Gastos (Ordem Decrescente) ---
    // Verifica se a variável de dados da tabela existe. Assumindo que é 'rows' ou similar.
    // Se a chamada for tab([...], rows), a variável é 'rows'. Vamos tentar deduzir da chamada.
    const varTabela = "VAR_TABELA_AQUI"; // Será substituído pelo script Python
    
    if (typeof varTabela !== 'undefined' && Array.isArray(varTabela) && varTabela.length > 1) {
        // Copia e converte os valores para número (ignorando a linha TOTAL)
        const dadosRanking = [];
        varTabela.forEach(r => {
            const nome = r[0];
            if (nome && nome.toUpperCase().includes('TOTAL')) return;
            
            const valorStr = r[1]; // Ex: "R$ 16.937.035,31"
            // Converte "R$ 16.937.035,31" -> 16937035.31
            const num = parseFloat(valorStr.replace('R$', '').replace(/\\./g, '').replace(',', '.').trim());
            
            if (!isNaN(num)) {
                dadosRanking.push({ nome: nome, valorStr: valorStr, valorNum: num, variacao: r[3] });
            }
        });
        
        // Ordena decrescente
        dadosRanking.sort((a, b) => b.valorNum - a.valorNum);
        
        H += sub('Ranking de Gastos (Maior para Menor)');
        const rowsRanking = dadosRanking.map((r, i) => [String(i + 1), r.nome, r.valorStr, r.variacao]);
        H += tab(['#', 'Centro de Custo', 'Gasto Atual', 'Variação (%)'], rowsRanking);
    }
"""

# Descobre o nome da variável usada na chamada da tabela (o segundo argumento)
# A regex captura algo como "H += tab([...], NOME_VARIAVEL);"
match_var = re.search(r"tab\(\[[^\]]+\],\s*([a-zA-Z0-9_]+)\)", chamada_tabela)
nome_variavel = match_var.group(1) if match_var else "rows"

# Substitui o placeholder pelo nome real da variável
codigo_ranking = codigo_ranking.replace('"VAR_TABELA_AQUI"', nome_variavel).replace("varTabela", nome_variavel)

# 5. Substitui a chamada da tabela original por ela mesma + o código de ranking
bloco_novo = bloco_secao11.replace(
    chamada_tabela,
    chamada_tabela + "\n" + codigo_ranking
)

# 6. Atualiza o HTML
html = html.replace(bloco_secao11, bloco_novo)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print(f"[OK] Ranking inserido na Seção 11 usando a variável '{nome_variavel}'.")
