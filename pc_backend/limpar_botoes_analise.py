c = open('../pc_frontend/analise_centro_custos.html', encoding='utf-8-sig').read()

# 1. Remover o botão "Configurações"
c = c.replace(
    '<button class="btn btn-config" onclick="window.location.href=\'/configuracoes_custo_pessoal\'">Configurações</button>\n            ',
    ''
)

# 2. Remover o botão "Importar CSV" e o input file associado
c = c.replace(
    '<button class="btn btn-importar" onclick="document.getElementById(\'file-csv\').click()" style="background-color: #6f42c1; color: white;">Importar CSV</button>\n            ',
    ''
)
c = c.replace(
    '<input type="file" id="file-csv" accept=".csv" style="display: none;" onchange="importarCSV(event)">\n            ',
    ''
)

# 3. Remover a função importarCSV (já que o botão não existe mais)
import re
c = re.sub(r'async function importarCSV\(event\) \{.*?\n        \}\n', '', c, flags=re.DOTALL)

open('../pc_frontend/analise_centro_custos.html', 'w', encoding='utf-8').write(c)
print("[OK] Botoes 'Configuracoes' e 'Importar CSV' removidos da tela de Analise!")
