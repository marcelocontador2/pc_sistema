arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

# Localiza o bloco 9 inteiro
padrao = re.compile(
    r"(//\s*9\.\s*ÍNDICES.*?)(?=\n\s*//\s*10\.|\Z)",
    re.DOTALL | re.IGNORECASE
)
m = padrao.search(html)
if not m:
    print("[ERRO] Bloco 9 não encontrado.")
    raise SystemExit

bloco_original = m.group(0)

# Remove qualquer tentativa anterior de memória de cálculo
bloco_original = re.sub(r"// --- Memória de Cálculo ---.*?H \+= '</tbody></table>';", "", bloco_original, flags=re.DOTALL)

# Adiciona a memória de cálculo de forma robusta, logo ANTES do fechamento final do bloco
# (antes do último fechamento de chaves ou do else)

memoria = """
// --- Memória de Cálculo ---
H += sub('Memória de Cálculo');
// Valores extraídos da base para as fórmulas
const vCaixa = 186838676.59;
const vAtivoCirc = 301495379.14;
const vEstoques = 185551.08;
const vRealizavel = 184825447.50;
const vAtivoNaoCirc = 315111651.51;
const vPassivoCirc = 129453937.95;
const vPassivoNaoCirc = 11725635.04;
const vPassivoTotal = 12238786.04; // Para o cálculo de endividamento
const vAtivoTotal = 616607030.65;
const vPL = 604368244.61;

const formulas = [
    ['Liquidez Imediata', 'Caixa / Passivo Circulante', 
     `R$ ${vCaixa.toLocaleString('pt-BR', {minimumFractionDigits:2})} / R$ ${vPassivoCirc.toLocaleString('pt-BR', {minimumFractionDigits:2})}`, 
     (vCaixa / vPassivoCirc).toFixed(2)],
    
    ['Liquidez Corrente', 'Ativo Circulante / Passivo Circulante', 
     `R$ ${vAtivoCirc.toLocaleString('pt-BR', {minimumFractionDigits:2})} / R$ ${vPassivoCirc.toLocaleString('pt-BR', {minimumFractionDigits:2})}`, 
     (vAtivoCirc / vPassivoCirc).toFixed(2)],
    
    ['Liquidez Seca', '(Ativo Circulante - Estoques) / Passivo Circulante', 
     `(R$ ${vAtivoCirc.toLocaleString('pt-BR', {minimumFractionDigits:2})} - R$ ${vEstoques.toLocaleString('pt-BR', {minimumFractionDigits:2})}) / R$ ${vPassivoCirc.toLocaleString('pt-BR', {minimumFractionDigits:2})}`, 
     ((vAtivoCirc - vEstoques) / vPassivoCirc).toFixed(2)],
    
    ['Liquidez Geral', '(Ativo Circ. + Realizável LP) / (Passivo Circ. + Passivo Não Circ.)', 
     `(R$ ${vAtivoCirc.toLocaleString('pt-BR', {minimumFractionDigits:2})} + R$ ${vRealizavel.toLocaleString('pt-BR', {minimumFractionDigits:2})}) / (R$ ${vPassivoCirc.toLocaleString('pt-BR', {minimumFractionDigits:2})} + R$ ${vPassivoNaoCirc.toLocaleString('pt-BR', {minimumFractionDigits:2})})`, 
     ((vAtivoCirc + vRealizavel) / (vPassivoCirc + vPassivoNaoCirc)).toFixed(2)],
     
    ['Endividamento Geral', 'Passivo Total / Ativo Total', 
     `R$ ${vPassivoTotal.toLocaleString('pt-BR', {minimumFractionDigits:2})} / R$ ${vAtivoTotal.toLocaleString('pt-BR', {minimumFractionDigits:2})}`, 
     (vPassivoTotal / vAtivoTotal * 100).toFixed(2) + '%'],
     
    ['Part. Capital de Terceiros', '(Passivo Circ. + Passivo Não Circ.) / PL', 
     `(R$ ${vPassivoCirc.toLocaleString('pt-BR', {minimumFractionDigits:2})} + R$ ${vPassivoNaoCirc.toLocaleString('pt-BR', {minimumFractionDigits:2})}) / R$ ${vPL.toLocaleString('pt-BR', {minimumFractionDigits:2})}`, 
     ((vPassivoCirc + vPassivoNaoCirc) / vPL * 100).toFixed(2) + '%'],
     
    ['Imobilização do PL', 'Ativo Não Circulante / PL', 
     `R$ ${vAtivoNaoCirc.toLocaleString('pt-BR', {minimumFractionDigits:2})} / R$ ${vPL.toLocaleString('pt-BR', {minimumFractionDigits:2})}`, 
     (vAtivoNaoCirc / vPL * 100).toFixed(2) + '%']
];

H += '<table class="table" style="font-size: 9px; margin-top: 10px; width: 100%; border-collapse: collapse;">';
H += '<thead><tr style="background:#0a2b5c; color:#fff;"><th style="padding:4px; text-align:left;">Índice</th><th style="padding:4px; text-align:left;">Fórmula</th><th style="padding:4px; text-align:left;">Cálculo</th><th style="padding:4px; text-align:right;">Resultado</th></tr></thead><tbody>';
formulas.forEach((f, i) => {
    const bg = i % 2 === 0 ? '#f8f9fa' : '#fff';
    H += `<tr style="background:${bg}; border-bottom:1px solid #ddd;"><td style="padding:4px;"><b>${f[0]}</b></td><td style="padding:4px;">${f[1]}</td><td style="padding:4px; color:#555;">${f[2]}</td><td style="padding:4px; text-align:right;"><b>${f[3]}</b></td></tr>`;
});
H += '</tbody></table>';
"""

# Estratégia infalível: substituir o final do bloco original
# Vamos procurar a última ocorrência de '}' ou '});' no bloco e inserir antes
if "} else { H += '<p>Módulo não encontrado.</p>'; }" in bloco_original:
    bloco_ajustado = bloco_original.replace(
        "} else { H += '<p>Módulo não encontrado.</p>'; }",
        memoria + "\n} else { H += '<p>Módulo não encontrado.</p>'; }"
    )
else:
    # Se não tiver o else, insere no final do bloco (antes do fechamento)
    idx = bloco_original.rfind('}')
    if idx != -1:
        bloco_ajustado = bloco_original[:idx] + memoria + bloco_original[idx:]
    else:
        bloco_ajustado = bloco_original + memoria

html = html.replace(bloco_original, bloco_ajustado)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Memória de Cálculo adicionada com valores fixos da imagem.")
