c = open('main.py', encoding='utf-8-sig').read()

# Substitui o período anterior padrão na rota
c = c.replace(
    'periodo_anterior: str = "2026-TRIMESTRE-2"',
    'periodo_anterior: str = "2025-TRIMESTRE-3"'
)

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] Período anterior padrão ajustado para 2025-TRIMESTRE-3!")
