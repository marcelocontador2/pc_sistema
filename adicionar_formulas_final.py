arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

import re

# 1. Remove qualquer tentativa anterior de memória de cálculo
html = re.sub(r"// --- Memória de Cálculo ---.*?H \+= '</tbody></table>';", "", html, flags=re.DOTALL)

# 2. Define o bloco de memória de cálculo
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
const vPassivoTotal = 12238786.04; 
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

# 3. Estratégia 1: Tentar achar a seção 9 e inserir logo antes da tag </body> ou do script final
# Como o bloco 9 não foi encontrado pelo regex, vamos procurar o final do script JS.
# Normalmente, o template tem 'document.getElementById' ou 'window.onload' ou um fechamento de script.
# Vamos procurar o último '}' que fecha a função que monta o H, ou simplesmente injetar antes do fechamento do body.

# Vamos procurar o padrão de fechamento do script (</script> ou </body>)
# Mas precisamos garantir que o código JS seja executado.
# Vamos injetar logo antes do último `}` do template, ou antes de `</script>`.

# Tenta encontrar onde o script termina e insere o código lá dentro
# (assumindo que o template tem um bloco <script> ... </script> que monta o H)

if "</script>" in html:
    # Encontra a última ocorrência de </script> e injeta antes (dentro do script)
    idx = html.rfind("</script>")
    # Injeta o código JS, mas precisamos garantir que não quebre a sintaxe.
    # Vamos injetar logo antes do fechamento.
    html = html[:idx] + memoria + "\n" + html[idx:]
    with open(arq, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] Memória de Cálculo injetada no final do script (antes de </script>).")
else:
    # Fallback: injetar antes do </body>
    idx = html.rfind("</body>")
    if idx != -1:
        html = html[:idx] + "<script>" + memoria + "</script>\n" + html[idx:]
        with open(arq, "w", encoding="utf-8") as f:
            f.write(html)
        print("[OK] Memória de Cálculo injetada antes de </body> (via novo script).")
    else:
        print("[ERRO] Não foi possível encontrar o local de injeção.")
