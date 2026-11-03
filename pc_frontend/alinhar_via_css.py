c = open('analise_comparativo_receitas.html', encoding='utf-8-sig').read()

# 1. Adiciona a regra CSS para alinhar as colunas (sem tocar no JavaScript)
css_alinhamento = """
        /* Alinhamento de tabelas */
        table th:not(:first-child), table td:not(:first-child) {
            text-align: right !important;
        }
"""
if 'table td:not(:first-child)' not in c:
    c = c.replace('</style>', css_alinhamento + '\n    </style>')

open('analise_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
print("[OK] CSS de alinhamento aplicado com segurança!")
