import re

c = open('relatorio_final.html', encoding='utf-8-sig').read()

# Remove o CSS @media print antigo (que estava quebrando a tela)
c = re.sub(r'@media print \{.*?\n        \}', '', c, flags=re.DOTALL)

# Adiciona um novo @media print, mais seguro
css_print = """
        @media print {
            .page {
                page-break-after: always;
                height: auto;
                min-height: 100vh;
            }
            .page:last-child {
                page-break-after: auto;
            }
            .btn-salvar {
                display: none !important;
            }
            body {
                margin: 0;
                padding: 0;
            }
        }
"""

# Adiciona o novo CSS no final do <style>
c = c.replace('</style>', css_print + '</style>')

open('relatorio_final.html', 'w', encoding='utf-8').write(c)
print("[OK] CSS @media print corrigido!")
