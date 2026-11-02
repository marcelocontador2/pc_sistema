c = open('main.py', encoding='utf-8-sig').read()

# Remove a chave duplicada
c = c.replace(
    '''        "variacao_pct": ((atual["total"] - anterior["total"]) / anterior["total"] * 100) if anterior["total"] > 0 else 0
    }
    }''',
    '''        "variacao_pct": ((atual["total"] - anterior["total"]) / anterior["total"] * 100) if anterior["total"] > 0 else 0
    }'''
)

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] Chave duplicada removida!")
