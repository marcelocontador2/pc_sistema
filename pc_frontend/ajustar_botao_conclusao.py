c = open('relatorio_final.html', encoding='utf-8-sig').read()

# 1. Ajusta a classe .page para não cortar o conteúdo (permite rolagem interna se necessário)
c = c.replace(
    '''.page {
            padding: 50px 60px;
            page-break-after: always;
            position: relative;
            box-sizing: border-box;
            height: 100vh;
            overflow: hidden;
        }''',
    '''.page {
            padding: 50px 60px;
            page-break-after: always;
            position: relative;
            box-sizing: border-box;
            min-height: 100vh;
            height: auto;
            overflow: visible;
        }'''
)

# 2. Adiciona um estilo específico para a página de conclusão
c = c.replace(
    '<!-- CONCLUSÃO -->\n    <div class="page">',
    '<!-- CONCLUSÃO -->\n    <div class="page" style="display: flex; flex-direction: column; justify-content: space-between;">'
)

open('relatorio_final.html', 'w', encoding='utf-8').write(c)
print("[OK] CSS da página de conclusão ajustado! O botão deve aparecer agora.")
