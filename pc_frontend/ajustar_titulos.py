import re

c = open('analise_comparativo_despesas.html', encoding='utf-8').read()

# 1. Atualizar o CSS da classe .section-title
css_antigo = r'\.section-title\s*\{[^}]+\}'
css_novo = """.section-title { 
            font-size: 16px; 
            font-weight: 700; 
            margin: 30px 0 15px 0; 
            color: #ffffff; 
            background-color: var(--primary); 
            text-align: center; 
            padding: 10px 15px; 
            border-radius: 4px; 
            text-transform: uppercase; 
            letter-spacing: 1px; 
        }"""
c = re.sub(css_antigo, css_novo, c)

# 2. Remover os números dos títulos no JavaScript
c = c.replace('"1. Despesas Correntes', '"Despesas Correntes')
c = c.replace('"2. Despesas de Capital', '"Despesas de Capital')

# (O título do Total Geral já não tinha número, então mantemos ele como está)

open('analise_comparativo_despesas.html', 'w', encoding='utf-8').write(c)
print("[OK] Títulos atualizados com tarja azul, fonte branca e sem números!")
