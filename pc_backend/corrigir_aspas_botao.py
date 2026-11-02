c = open('../pc_frontend/analise_centro_custos.html', encoding='utf-8-sig').read()

# Corrige as aspas ausentes no onclick
c = c.replace(
    'onclick="document.getElementById(file-csv).click()"',
    'onclick="document.getElementById(\'file-csv\').click()"'
)

open('../pc_frontend/analise_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Aspas do onclick corrigidas!")
