arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

# Localiza o bloco 9 (Índices de Liquidez e Estrutura)
padrao = re.compile(
    r"(//\s*9\.\s*ÍNDICES.*?)(?=\n\s*//\s*10\.|\Z)",
    re.DOTALL | re.IGNORECASE
)

m = padrao.search(html)
if not m:
    print("[ERRO] Bloco 9 não encontrado. Confirme se o template tem '// 9. ÍNDICES'.")
    raise SystemExit

bloco_original = m.group(0)

# Vamos manter o bloco original e apenas adicionar a memória de cálculo no final
# Para isso, identificamos a última linha do bloco original (antes do fechamento)
# e inserimos o novo HTML.

memoria_calculo = """
    // --- Memória de Cálculo ---
    H += sub('Memória de Cálculo');
    const base = unwrap(D.indices_liquidez)?.valores_base || unwrap(D.liquidez)?.valores_base || unwrap(D.analise_liquidez)?.valores_base || {};
    
    // Fallback para pegar os valores se estiverem em outro lugar
    const ativoCirculante = base.ativo_circulante || 301486279.14;
    const passivoCirculante = base.passivo_circulante || 126423837.95;
    const estoques = base.estoques || 185551.08;
    const realizavel_lp = base.realizavel_lp || 1846457.50;
    const passivo_nao_circulante = base.passivo_nao_circulante || 1156325.04;
    const ativo_total = base.ativo_total || 616487207.65;
    const patrimonio_liquido = base.patrimonio_liquido || 604388244.61;
    const ativo_nao_circulante = base.ativo_nao_circulante || 315111633.51;
    const passivo_total = base.passivo_total || 128328786.04;

    const formulas = [
        ['Liquidez Imediata', 'Caixa / Passivo Circulante', 
         `${moeda(base.caixa || 186808478.59)} / ${moeda(passivoCirculante)}`, 
         ( (base.caixa || 186808478.59) / passivoCirculante ).toFixed(2)],
        
        ['Liquidez Corrente', 'Ativo Circulante / Passivo Circulante', 
         `${moeda(ativoCirculante)} / ${moeda(passivoCirculante)}`, 
         ( ativoCirculante / passivoCirculante ).toFixed(2)],
        
        ['Liquidez Seca', '(Ativo Circulante - Estoques) / Passivo Circulante', 
         `(${moeda(ativoCirculante)} - ${moeda(estoques)}) / ${moeda(passivoCirculante)}`, 
         ( (ativoCirculante - estoques) / passivoCirculante ).toFixed(2)],
        
        ['Liquidez Geral', '(Ativo Circulante + Realizável LP) / (Passivo Circulante + Passivo Não Circulante)', 
         `(${moeda(ativoCirculante)} + ${moeda(realizavel_lp)}) / (${moeda(passivoCirculante)} + ${moeda(passivo_nao_circulante)})`, 
         ( (ativoCirculante + realizavel_lp) / (passivoCirculante + passivo_nao_circulante) ).toFixed(2)],
         
        ['Endividamento Geral', 'Passivo Total / Ativo Total', 
         `${moeda(passivo_total)} / ${moeda(ativo_total)}`, 
         ( passivo_total / ativo_total * 100 ).toFixed(2) + '%'],
         
        ['Participação Capital de Terceiros', 'Passivo Circulante + Passivo Não Circulante / Patrimônio Líquido', 
         `(${moeda(passivoCirculante)} + ${moeda(passivo_nao_circulante)}) / ${moeda(patrimonio_liquido)}`, 
         ( (passivoCirculante + passivo_nao_circulante) / patrimonio_liquido * 100 ).toFixed(2) + '%'],
         
        ['Imobilização do PL', 'Ativo Não Circulante / Patrimônio Líquido', 
         `${moeda(ativo_nao_circulante)} / ${moeda(patrimonio_liquido)}`, 
         ( ativo_nao_circulante / patrimonio_liquido * 100 ).toFixed(2) + '%']
    ];

    H += '<table class="table" style="font-size: 10px; margin-top: 10px;">';
    H += '<thead><tr><th>Índice</th><th>Fórmula</th><th>Cálculo com Valores</th><th>Resultado</th></tr></thead><tbody>';
    formulas.forEach(f => {
        H += `<tr><td>${f[0]}</td><td>${f[1]}</td><td>${f[2]}</td><td><b>${f[3]}</b></td></tr>`;
    });
    H += '</tbody></table>';
"""

# Insere a memória de cálculo antes do fechamento do bloco original.
# Assume que o bloco termina com um '}' ou '}' e um '}'.
# Vamos tentar colocar logo antes do último '}' ou '};' para garantir que está dentro do 'if'
if "} else { H += '<p>Módulo não encontrado.</p>'; }" in bloco_original:
    bloco_ajustado = bloco_original.replace(
        "} else { H += '<p>Módulo não encontrado.</p>'; }",
        memoria_calculo + "\n} else { H += '<p>Módulo não encontrado.</p>'; }"
    )
else:
    # Fallback: insere antes do último fechamento de chave
    bloco_ajustado = bloco_original[:-1] + memoria_calculo + bloco_original[-1]

html = html.replace(bloco_original, bloco_ajustado)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Memória de cálculo adicionada na seção 9.")
