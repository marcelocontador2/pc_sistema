from pathlib import Path
import re

arquivo = Path("pc_frontend/custo_pessoal_pdf_completo.html")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Corrigir o texto "(50% da RCL)" para mostrar o percentual dinamico
conteudo = conteudo.replace(
    "Limite Resolução Cofen 814/2026 (50% da RCL)",
    "Limite Resolução Cofen 814/2026 (<span id='pdf-limite-pct-text'>50%</span> da RCL)"
)

# 2. Corrigir o percentual ao lado do limite (que estava fixo em 50,00%)
trecho_antigo_pct = '<td class="right">50,00%</td>'
trecho_novo_pct = '<td class="right" id="pdf-resumo-limite-pct">50,00%</td>'
if trecho_antigo_pct in conteudo:
    conteudo = conteudo.replace(trecho_antigo_pct, trecho_novo_pct, 1)

# 3. Atualizar o JS para preencher o percentual do limite corretamente
# (o JS atual calcula com "limite_pct * 100", mas o "limite_pct" pode estar vindo errado)
# Vamos forçar o uso de d.limite_pct
trecho_js = "document.getElementById('pdf-limite').innerText = fmt(limite) + ' (' + (limite_pct * 100).toFixed(2) + '%)';"
trecho_js_novo = "document.getElementById('pdf-limite').innerText = fmt(limite); var pctEl = document.getElementById('pdf-limite-pct-text'); if (pctEl) pctEl.innerText = (limite_pct * 100).toFixed(2) + '%';"

if trecho_js in conteudo:
    conteudo = conteudo.replace(trecho_js, trecho_js_novo, 1)
    print("OK: JS do limite corrigido (mostra o percentual dinamico)!")

# 4. Atualizar o JS para preencher o percentual do resumo (ao lado do limite)
trecho_js2 = "document.getElementById('pdf-resumo-limite').innerText = fmt(limite);"
if trecho_js2 in conteudo:
    novo_js2 = "document.getElementById('pdf-resumo-limite').innerText = fmt(limite); var pctEl2 = document.getElementById('pdf-resumo-limite-pct'); if (pctEl2) pctEl2.innerText = (limite_pct * 100).toFixed(2) + '%';"
    conteudo = conteudo.replace(trecho_js2, novo_js2, 1)
    print("OK: JS do resumo corrigido (percentual dinamico)!")

# 5. Garantir que limite_pct esta definido (fallback para 0.5)
if "const limite_pct = d.limite_pct" not in conteudo:
    conteudo = conteudo.replace(
        "const limite = d.limite_atual || (rcl * (d.limite_pct || 0.5));",
        "const limite = d.limite_atual || (rcl * (d.limite_pct || 0.5));\n                    const limite_pct = d.limite_pct || 0.5;"
    )
    print("OK: limite_pct garantido no JS!")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: PDF completo atualizado!")
