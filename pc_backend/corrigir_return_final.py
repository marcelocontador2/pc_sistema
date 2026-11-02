c = open('main.py', encoding='utf-8-sig').read()

# Corrige o return final (adiciona a chave que falta)
c = c.replace(
    '''        "variacao_total": atual["total"] - anterior["total"],
        "variacao_pct": ((atual["total"] - anterior["total"]) / anterior["total"] * 100) if anterior["total"] > 0 else 0''',
    '''        "variacao_total": atual["total"] - anterior["total"],
        "variacao_pct": ((atual["total"] - anterior["total"]) / anterior["total"] * 100) if anterior["total"] > 0 else 0
    }'''
)

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] Return final corrigido!")
