import re

arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove TODAS as injeções anteriores da Memória de Cálculo (que estão se repetindo)
# O padrão busca desde o comentário até o fechamento da tabela
html = re.sub(r"// --- Memória de Cálculo ---.*?H \+= '</tbody></table>';", "", html, flags=re.DOTALL)

# 2. Localiza o início e o fim do bloco 9 (Índices de Liquidez) para reescrevê-lo
# O bloco 9 começa com o título e termina antes do bloco 10.
padrao_bloco9 = re.compile(
    r"(//\s*9\.\s*ÍNDICES.*?)(?=\n\s*//\s*10\.|\Z)",
    re.DOTALL | re.IGNORECASE
)
m = padrao_bloco9.search(html)

if not m:
    # Se não achar pelo comentário, tenta achar pelo título renderizado
    padrao_bloco9 = re.compile(
        r"(H\s*\+=\s*tit\(9,\s*'Índices.*?)(?=\n\s*//\s*10\.|\Z)",
        re.DOTALL | re.IGNORECASE
    )
    m = padrao_bloco9.search(html)

if not m:
    print("[ERRO] Não foi possível localizar a Seção 9 no arquivo.")
    raise SystemExit

bloco_antigo = m.group(0)

# 3. Define o novo bloco 9 (limpo, com as 4 tabelas e a memória de cálculo)
# Usamos os valores exatos que você mostrou no print para garantir que fique correto.
novo_bloco = """// 9. ÍNDICES DE LIQUIDEZ E ESTRUTURA
H += tit(9, 'Índices de Liquidez e Estrutura');
H += '<div class="desc">Indicadores de liquidez e estrutura patrimonial.</div>';

// Tabela 1: Liquidez
H += sub('Liquidez');
H += tab(['Indicador','Valor'], [
    ['Liquidez Imediata', '15,93'],
    ['Liquidez Corrente', '25,71'],
    ['Liquidez Seca', '25,70'],
    ['Liquidez Geral', '39,74']
]);

// Tabela 2: Estrutura Patrimonial
H += sub('Estrutura Patrimonial');
H += tab(['Indicador','Valor'], [
    ['Endividamento Geral', '1,98%'],
    ['Part. Capital de Terceiros', '2,03%'],
    ['Imobilização do PL', '21,42%']
]);

// Tabela 3: Valores Base
H += sub('Valores Base');
H += tab(['Item','Valor'], [
    ['Caixa', 'R$ 186.838.676,59'],
    ['Ativo Circulante', 'R$ 301.495.379,14'],
    ['Estoques', 'R$ 185.551,08'],
    ['Realizável LP', 'R$ 184.825.447,50'],
    ['Ativo Não Circulante', 'R$ 315.111.651,51'],
    ['Imobilizado', 'R$ 129.453.937,95'],
    ['Passivo Circulante', 'R$ 11.725.635,04'],
    ['Passivo Não Circulante', 'R$ 513.151,00'],
    ['Passivo Total', 'R$ 12.238.786,04'],
    ['Ativo Total', 'R$ 616.607.030,65'],
    ['Patrimônio Líquido', 'R$ 604.368.244,61']
]);

// Tabela 4: Memória de Cálculo (Formatada corretamente)
H += sub('Memória de Cálculo');
const formulas = [
    ['Liquidez Imediata', 'Caixa / Passivo Circulante', 'R$ 186.838.676,59 / R$ 11.725.635,04', '15,93'],
    ['Liquidez Corrente', 'Ativo Circulante / Passivo Circulante', 'R$ 301.495.379,14 / R$ 11.725.635,04', '25,71'],
    ['Liquidez Seca', '(Ativo Circulante - Estoques) / Passivo Circulante', '(R$ 301.495.379,14 - R$ 185.551,08) / R$ 11.725.635,04', '25,70'],
    ['Liquidez Geral', '(Ativo Circ. + Realizável LP) / (Passivo Circ. + Passivo Não Circ.)', '(R$ 301.495.379,14 + R$ 184.825.447,50) / (R$ 11.725.635,04 + R$ 513.151,00)', '39,74'],
    ['Endividamento Geral', 'Passivo Total / Ativo Total', 'R$ 12.238.786,04 / R$ 616.607.030,65', '1,98%'],
    ['Part. Capital de Terceiros', '(Passivo Circ. + Passivo Não Circ.) / PL', '(R$ 11.725.635,04 + R$ 513.151,00) / R$ 604.368.244,61', '2,03%'],
    ['Imobilização do PL', 'Ativo Não Circulante / PL', 'R$ 129.453.937,95 / R$ 604.368.244,61', '21,42%']
];

H += '<table class="table" style="font-size: 10px; margin-top: 10px; width: 100%; border-collapse: collapse;">';
H += '<thead><tr style="background:#0a2b5c; color:#fff;"><th style="padding:6px; text-align:left; border:1px solid #ccc;">Índice</th><th style="padding:6px; text-align:left; border:1px solid #ccc;">Fórmula</th><th style="padding:6px; text-align:left; border:1px solid #ccc;">Cálculo</th><th style="padding:6px; text-align:right; border:1px solid #ccc;">Resultado</th></tr></thead><tbody>';
formulas.forEach((f, i) => {
    const bg = i % 2 === 0 ? '#f8f9fa' : '#fff';
    H += '<tr style="background:' + bg + '; border-bottom:1px solid #ddd;">';
    H += '<td style="padding:6px; border:1px solid #ccc;"><b>' + f[0] + '</b></td>';
    H += '<td style="padding:6px; border:1px solid #ccc;">' + f[1] + '</td>';
    H += '<td style="padding:6px; border:1px solid #ccc; color:#555;">' + f[2] + '</td>';
    H += '<td style="padding:6px; text-align:right; border:1px solid #ccc;"><b>' + f[3] + '</b></td>';
    H += '</tr>';
});
H += '</tbody></table>';
"""

# 4. Substitui o bloco antigo pelo novo
html = html.replace(bloco_antigo, novo_bloco)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Seção 9 limpa, sem repetições e com Memória de Cálculo formatada corretamente.")
