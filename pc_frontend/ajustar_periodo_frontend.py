c = open('relatorio_centro_custos.html', encoding='utf-8-sig').read()

c = c.replace(
    "const periodoAnterior = params.get('periodo_anterior') || '2026-TRIMESTRE-2';",
    "const periodoAnterior = params.get('periodo_anterior') || '2025-TRIMESTRE-3';"
)

open('relatorio_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Frontend ajustado para buscar 2025-TRIMESTRE-3!")
