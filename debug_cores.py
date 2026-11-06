arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# Adiciona um log no console do navegador para descobrirmos a estrutura
script_debug = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    if (typeof D !== 'undefined' && D.comparativo_receitas && D.comparativo_receitas.atual && D.comparativo_receitas.atual.cores) {
        console.log('=== ESTRUTURA DE UMA COREN ===');
        console.log(D.comparativo_receitas.atual.cores[0]);
        console.log('=== TODAS AS CHAVES ===');
        console.log(Object.keys(D.comparativo_receitas.atual.cores[0]));
    }
});
</script>
"""
# Injeta o script logo antes do fechamento do body
if '</body>' in html:
    html = html.replace('</body>', script_debug + '\n</body>')

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Script de debug injetado no template.")
