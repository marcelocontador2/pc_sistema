import re

arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# Localiza o bloco do Sumário (que está corrompido)
# Ele geralmente é gerado por um loop for ou map
padrao_sumario = re.compile(
    r"(H\s*\+=\s*tit\(2,\s*['\"]Sumário['\"]\);.*?)(?=\n\s*//\s*3\.|\Z)",
    re.DOTALL | re.IGNORECASE
)
m = padrao_sumario.search(html)

if m:
    bloco_antigo = m.group(0)
    # Substitui por um sumário limpo e simples
    novo_sumario = """// 2. SUMÁRIO
H += tit(2, 'Sumário');
H += '<div class="desc">Índice do relatório.</div>';
const sumario = [
    ['1', 'Capa'],
    ['2', 'Sumário'],
    ['3', 'Análise do Balanço Orçamentário'],
    ['4', 'Análise do Balanço Financeiro'],
    ['5', 'Análise do Balanço Patrimonial'],
    ['6', 'Análise das Variações Patrimoniais (DVP)'],
    ['7', 'Comparativo de Receitas'],
    ['8', 'Comparativo de Despesas'],
    ['9', 'Índices de Liquidez e Estrutura'],
    ['10', 'Análise por Centro de Custos'],
    ['11', 'Análise por Centro de Custos (Ranking)'],
    ['12', 'Conclusão'],
    ['13', 'Parecer do Contador'],
    ['14', 'Assinatura']
];
const rowsSumario = sumario.map(s => [s[0], s[1]]);
H += tab(['#', 'Seção'], rowsSumario);
"""
    html = html.replace(bloco_antigo, novo_sumario)
    print("[OK] Sumário corrigido.")
else:
    print("[AVISO] Bloco do Sumário não encontrado. O problema pode estar em outro lugar.")

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)
