import re

c = open('relatorio_final.html', encoding='utf-8-sig').read()

# 1. Adiciona uma classe "nota-instrucao" na Nota 5 para identificá-la
c = c.replace(
    '<div class="nota" style="margin-top: 25px;">\n            <strong>Nota 5:</strong>',
    '<div class="nota nota-instrucao" style="margin-top: 25px;">\n            <strong>Nota 5:</strong>'
)

# 2. Adiciona a regra CSS para esconder essa nota na impressão
if '.nota-instrucao' not in c.split('@media print')[1] if '@media print' in c else True:
    css_print = """
        @media print {
            .nota-instrucao { display: none !important; }
        }
    """
    c = c.replace('</style>', css_print + '\n    </style>')

open('relatorio_final.html', 'w', encoding='utf-8').write(c)
print("[OK] Nota 5 será escondida na impressão!")
